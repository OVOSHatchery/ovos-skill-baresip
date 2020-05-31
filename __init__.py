from mycroft.skills.core import FallbackSkill, intent_file_handler, \
    intent_handler
from mycroft.skills.skill_data import read_vocab_file
import time
from mycroft.util import camel_case_split, create_daemon
from baresipy.contacts import ContactList
from baresipy import BareSIP
from itertools import chain
from time import sleep


class SIPSkill(FallbackSkill):
    def __init__(self):
        super(SIPSkill, self).__init__(name='SIPSkill')
        # skill settings defaults
        if "intercept_allowed" not in self.settings:
            self.settings["intercept_allowed"] = True
        if "confirm_operations" not in self.settings:
            self.settings["confirm_operations"] = True
        if "debug" not in self.settings:
            self.settings["debug"] = True
        if "priority" not in self.settings:
            self.settings["priority"] = 50
        if "timeout" not in self.settings:
            self.settings["timeout"] = 15

        # auto answer incoming calls
        if "auto_answer" not in self.settings:
            self.settings["auto_answer"] = False
        if "auto_reject" not in self.settings:
            self.settings["auto_reject"] = False
        if "auto_speech" not in self.settings:
            self.settings["auto_speech"] = "I am busy, try again later"

        # web ui contacts management
        self.settings["add_contact"] = False
        self.settings["delete_contact"] = False
        if "contact_name" not in self.settings:
            self.settings["contact_name"] = None
        if "contact_address" not in self.settings:
            self.settings["contact_address"] = None

        # sip creds
        if "user" not in self.settings:
            self.settings["user"] = None
        if "gateway" not in self.settings:
            self.settings["gateway"] = None
        if "password" not in self.settings:
            self.settings["password"] = None

        # events
        self.settings_change_callback = self._on_web_settings_change
        self.namespace = self.__class__.__name__.lower()
        self.skill_name = "Voice Over IP"

        # state trackers
        self._converse_keepalive = None
        self.on_hold = False
        self.muted = False
        self.intercepting_utterances = False
        self._old_settings = dict(self.settings)

        self.sip = None
        self.say_vocab = None
        self.cb = None
        self.contacts = ContactList("mycroft_sip")

    def initialize(self):
        self.register_fallback(self.handle_fallback,
                               int(self.settings["priority"]))
        self._converse_keepalive = create_daemon(self.converse_keepalive)

        say_voc = self.find_resource('and_say.voc', 'vocab')
        if say_voc:
            # load vocab and flatten into a simple list
            # TODO sort by length
            self.say_vocab = list(chain(*read_vocab_file(say_voc)))
        self.start_sip()

    def _on_web_settings_change(self):
        # TODO settings should be uploaded to backend when changed inside
        #  skill, but this functionality is gone,
        #  the issue here is with Selene, if anyone thinks of a  clever
        #  workaround let me know, currently this is WONTFIX, problem
        #  is on mycroft side
        if self.settings["add_contact"]:
            if self.settings["contact_name"]:
                self.add_new_contact(self.settings["contact_name"],
                                     self.settings["contact_address"])
                self.settings["add_contact"] = False
        if self.settings["delete_contact"]:
            if self.settings["contact_name"]:
                self.delete_contact(self.settings["contact_name"])
                self.settings["delete_contact"] = False

        if self.sip is None:
            self.start_sip()
        else:
            for k in ["user", "password", "gateway"]:
                if self.settings[k] != self._old_settings[k]:
                    self.speak_dialog("sip_restart")
                    self.sip.quit()
                    self.sip = None
                    self.intercepting_utterances = False  # just in case
                    self.start_sip()
                    break
        self._old_settings = dict(self.settings)

    def start_sip(self):
        if self.sip is not None:
            self.sip.quit()
            sleep(0.5)
        self.sip = BareSIP(self.settings["user"],
                           self.settings["password"],
                           self.settings["gateway"], block=False,
                           debug=self.settings["debug"])
        self.sip.handle_incoming_call = self.handle_incoming_call
        self.sip.handle_call_ended = self.handle_call_ended
        self.sip.handle_login_failure = self.handle_login_failure
        self.sip.handle_login_success = self.handle_login_success
        self.sip.handle_call_established = self.handle_call_established

    def get_intro_message(self):
        # welcome dialog on skill install
        self.speak_dialog("intro", {"skill_name": self.skill_name})

    # SIP
    def handle_call_established(self):
        if self.cb is not None:
            self.cb()
            self.cb = None

    def handle_login_success(self):
        self.speak_dialog("sip_login_success")

    def handle_login_failure(self):
        self.log.error("Log in failed!")
        self.sip.quit()
        self.sip = None
        self.intercepting_utterances = False  # just in case
        if self.settings["user"] is not None and \
                self.settings["gateway"] is not None and \
                self.settings["password"] is not None:
            self.speak_dialog("sip_login_fail")
        else:
            self.speak_dialog("credentials_missing")

    def handle_incoming_call(self, number):
        if self.settings["auto_answer"]:
            self.accept_call()
            self._wait_until_call_established()
            self.sip.speak(self.settings["auto_speech"])
            self.hang_call()
            self.log.info("Auto answered call")
            return
        if self.settings["auto_reject"]:
            self.log.info("Auto rejected call")
            self.hang_call()
            return
        contact = self.contacts.search_contact(number)
        if contact:
            self.speak_dialog("incoming_call", {"contact": contact["name"]},
                              wait=True)
        else:
            self.speak_dialog("incoming_call_unk", wait=True)
        self.intercepting_utterances = True

    def handle_call_ended(self, reason):
        self.log.info("Call ended")
        self.log.debug("Reason: " + reason)
        self.intercepting_utterances = False
        self.on_hold = False
        self.muted = False

    def accept_call(self):
        self.sip.accept_call()

    def hang_call(self):
        self.sip.hang()
        self.intercepting_utterances = False
        self.speak_dialog("call_finished")

    def add_new_contact(self, name, address, prompt=False):
        contact = self.contacts.get_contact(name)
        # new address
        if contact is None:
            self.log.info("Adding new contact {name}:{address}".format(
                name=name, address=address))
            self.contacts.add_contact(name, address)
            self.speak_dialog("contact_added", {"contact": name})
        # update contact (address exist)
        else:
            contact = self.contacts.search_contact(address)
            if prompt:
                if self.ask_yesno(self, "update_confirm",
                                  data={"contact": name}) == "no":
                    return
            self.log.info("Updating contact {name}:{address}".format(
                name=name, address=address))
            if name != contact["name"]:
                # new name (unique ID)
                self.contacts.remove_contact(contact["name"])
                self.contacts.add_contact(name, address)
                self.speak_dialog("contact_updated", {"contact": name})
            elif address != contact["url"]:
                # new address
                self.contacts.update_contact(name, address)
                self.speak_dialog("contact_updated", {"contact": name})

    def delete_contact(self, name, prompt=False):
        if self.contacts.get_contact(name):
            if prompt:
                if self.ask_yesno(self, "delete_confirm",
                                  data={"contact": name}) == "no":
                    return
            self.log.info("Deleting contact {name}".format(name=name))
            self.contacts.remove_contact(name)
            self.speak_dialog("contact_deleted", {"contact": name})

    # intents
    def handle_utterance(self, utterance):
        # handle both fallback and converse stage utterances
        # control ongoing calls here
        if self.intercepting_utterances:
            if self.voc_match(utterance, 'reject'):
                self.hang_call()
                self.speak_dialog("call_rejected")
            elif self.muted or self.on_hold:
                # allow normal mycroft interaction in these cases only
                return False
            elif self.voc_match(utterance, 'accept'):
                speech = None
                if self.say_vocab and self.voc_match(utterance, 'and_say'):
                    for word in self.say_vocab:
                        if word in utterance:
                            speech = utterance.split(word)[1]
                            break
                # answer call
                self.accept_call()
                if speech:
                    self._wait_until_call_established()
                    self.sip.speak(speech)
                    self.hang_call()
                else:
                    # User 2 User
                    pass
            elif self.voc_match(utterance, 'hold_call'):
                self.on_hold = True
                self.sip.hold()
                self.speak_dialog("call_on_hold")
            elif self.voc_match(utterance, 'mute'):
                self.muted = True
                self.sip.mute_mic()
                self.speak_dialog("call_muted")
            # if in call always intercept utterance / assume false activation
            return True
        return False

    def _wait_until_call_established(self):
        # TTS in voice call and hang
        while not self.sip.call_established:
            sleep(0.5)  # TODO timeout in case of errors

    @intent_file_handler("restart.intent")
    def handle_restart(self, message):
        if self.sip is not None:
            self.sip.stop()
            self.sip = None
        self.handle_login(message)

    @intent_file_handler("login.intent")
    def handle_login(self, message):
        if self.sip is None:
            if self.settings["gateway"]:
                self.speak_dialog("sip_login",
                                  {"gateway": self.settings["gateway"]})
                self.start_sip()
            else:
                self.speak_dialog("credentials_missing")
        else:
            self.speak_dialog("sip_running")
            if self.ask_yesno("want_restart") == "yes":
                self.handle_restart(message)

    @intent_file_handler("call.intent")
    def handle_call_contact(self, message):
        name = message.data["contact"]
        self.log.debug("Placing call to " + name)
        contact = self.contacts.get_contact(name)
        if contact is not None:
            self.speak_dialog("calling", {"contact": name}, wait=True)
            self.intercepting_utterances = True
            address = contact["url"]
            self.sip.call(address)
        else:
            self.speak_dialog("no_such_contact", {"contact": name})

    @intent_file_handler("call_and_say.intent")
    def handle_call_contact_and_say(self, message):
        utterance = message.data["speech"]

        def cb():
            self.sip.speak(utterance)
            self.hang_call()

        self.cb = cb
        self.handle_call_contact(message)

    @intent_file_handler("resume_call.intent")
    @intent_file_handler("unmute.intent")
    def handle_resume(self, message):
        # TODO can both happen at same time ?
        if self.on_hold:
            self.on_hold = False
            self.speak_dialog("resume_call", wait=True)
            self.sip.resume()
        elif self.muted:
            self.muted = False
            self.speak_dialog("unmute_call", wait=True)
            self.sip.unmute_mic()
        else:
            self.speak_dialog("no_call")

    @intent_file_handler("reject_all.intent")
    def handle_auto_reject(self, message):
        self.settings["auto_reject"] = True
        self.settings["auto_answer"] = False
        self.speak_dialog("rejecting_all")

    @intent_file_handler("answer_all.intent")
    def handle_auto_answer(self, message):
        self.settings["auto_answer"] = True
        self.settings["auto_reject"] = False
        self.speak_dialog("accept_all",
                          {"speech": self.settings["auto_speech"]})

    @intent_file_handler("answer_all_and_say.intent")
    def handle_auto_answer_with(self, message):
        self.settings["auto_speech"] = message.data["speech"]
        self.handle_auto_answer(message)

    @intent_file_handler("contacts_list.intent")
    def handle_list_contacts(self, message):
        users = self.contacts.list_contacts()
        self.speak_dialog("contacts_list")
        for user in users:
            self.speak(user["name"])

    @intent_file_handler("contacts_number.intent")
    def handle_number_of_contacts(self, message):
        users = self.contacts.list_contacts()
        self.speak_dialog("contacts_number", {"number": len(users)})

    @intent_file_handler("disable_auto.intent")
    def handle_no_auto_answering(self, message):
        self.settings["auto_answer"] = False
        self.settings["auto_reject"] = False
        self.speak_dialog("no_auto")

    # converse
    def converse_keepalive(self):
        while True:
            if self.settings["intercept_allowed"]:
                # avoid converse timed_out
                self.make_active()
            time.sleep(60)

    def converse(self, utterances, lang="en-us"):
        if self.settings["intercept_allowed"]:
            self.log.debug("{name}: Intercept stage".format(
                name=self.skill_name))
            return self.handle_utterance(utterances[0])
        return False

    # fallback
    def handle_fallback(self, message):
        utterance = message.data["utterance"]
        self.log.debug("{name}: Fallback stage".format(name=self.skill_name))
        return self.handle_utterance(utterance)

    # shutdown
    def stop_converse(self):
        if self._converse_keepalive is not None and \
                self._converse_keepalive.running:
            self._converse_keepalive.join(2)

    def shutdown(self):
        if self.sip is not None:
            self.sip.quit()
        self.stop_converse()
        super(SIPSkill, self).shutdown()


def create_skill():
    return SIPSkill()
