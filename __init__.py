from mycroft.skills.core import FallbackSkill, intent_file_handler, \
    intent_handler
from mycroft.skills.skill_data import read_vocab_file
import time
from mycroft.util import camel_case_split, create_daemon
from baresipy.contacts import ContactList
from baresipy import BareSIP
from itertools import chain
from time import sleep
from collections import defaultdict
from xml.etree import cElementTree as ET
import requests
from requests.auth import HTTPBasicAuth
from mycroft.messagebus.message import Message

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

        # sipxcom integration
        if "sipxcom_user" not in self.settings:
            self.settings["sipxcom_user"] = None
        if "sipxcom_gateway" not in self.settings:
            self.settings["sipxcom_gateway"] = None
        if "sipxcom_password" not in self.settings:
            self.settings["sipxcom_password"] = None
        if "sipxcom_sync" not in self.settings:
            self.settings["sipxcom_sync"] = False

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
        if self.settings["sipxcom_sync"]:
            self.sipxcom_sync()
            
        # Register GUI Events
        self.handle_gui_state("Clear")
        self.gui.register_handler("voip.jarbas.acceptCall", self.accept_call)
        self.gui.register_handler("voip.jarbas.hangCall", self.hang_call)
        self.gui.register_handler("voip.jarbas.muteCall", self.mute_call)
        self.gui.register_handler("voip.jarbas.unmuteCall", self.unmute_call)
        self.gui.register_handler("voip.jarbas.callContact", self.handle_call_contact_from_gui)
        self.gui.register_handler("voip.jarbas.updateConfig", self.handle_config_from_gui)
        self.add_event('skill-voip.jarbasskills.home', self.show_homescreen)
        
    def _on_web_settings_change(self):
        # TODO settings should be uploaded to backend when changed inside
        #  skill, but this functionality is gone,
        #  the issue here is with Selene, if anyone thinks of a  clever
        #  workaround let me know, currently this is WONTFIX, problem
        #  is on mycroft side
        if self.settings["delete_contact"] and self.settings["contact_name"] \
                != self._oldsettings["contact_name"]:
            self.delete_contact(self.settings["contact_name"])
            self.settings["delete_contact"] = False
        elif self.settings["add_contact"] and self.settings["contact_name"] \
                != self._oldsettings["contact_name"]:
            self.add_new_contact(self.settings["contact_name"],
                                 self.settings["contact_address"])
            self.settings["add_contact"] = False

        if self.settings["auto_reject"]:
            self.settings["auto_answer"] = False
        elif self.settings["auto_answer"]:
            self.settings["auto_reject"] = False

            if self.settings["auto_speech"] != \
                    self._old_settings["auto_speech"]:
                self.speak_dialog("accept_all",
                                  {"speech": self.settings["auto_speech"]})

        if self.settings["sipxcom_sync"]:
            self.sipxcom_sync()

        if self.sip is None:
            if self.settings["gateway"]:
                self.start_sip()
            else:
                self.speak_dialog("credentials_missing")
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
    def _wait_until_call_established(self):
        while not self.sip.call_established:
            sleep(0.5)  # TODO timeout in case of errors

    def accept_call(self):
        self.sip.accept_call()
        self.handle_gui_state("Connected")

    def hang_call(self):
        self.sip.hang()
        self.intercepting_utterances = False
        
    def mute_call(self):
        self.gui["call_muted"] = True
        self.sip.mute_mic()
    
    def unmute_call(self):
        self.gui["call_muted"] = False
        self.sip.unmute_mic()

    def add_new_contact(self, name, address, prompt=False):
        name = name.replace("_", " ").replace("-", " ").strip()
        address = address.strip()
        contact = self.contacts.get_contact(name)
        # new address
        if contact is None:
            self.log.info("Adding new contact {name}:{address}".format(
                name=name, address=address))
            self.contacts.add_contact(name, address)
            self.speak_dialog("contact_added", {"contact": name}, wait=True)
        # update contact (address exist)
        else:
            contact = self.contacts.search_contact(address) or contact
            if prompt and \
                    (name != contact["name"] or address != contact["url"]):
                if self.ask_yesno("update_confirm",
                                  data={"contact": name}) == "no":
                    return
            self.log.info("Updating contact {name}:{address}".format(
                name=name, address=address))
            if name != contact["name"]:
                # new name (unique ID)
                self.contacts.remove_contact(contact["name"])
                self.contacts.add_contact(name, address)
                self.speak_dialog("contact_updated", {"contact": name},
                                  wait=True)
            elif address != contact["url"]:
                # new address
                self.contacts.update_contact(name, address)
                self.speak_dialog("contact_updated", {"contact": name},
                                  wait=True)

    def delete_contact(self, name, prompt=False):
        name = name.replace("_", " ").replace("-", " ").strip()
        if self.contacts.get_contact(name):
            if prompt:
                if self.ask_yesno("delete_confirm",
                                  data={"contact": name}) == "no":
                    return
            self.log.info("Deleting contact {name}".format(name=name))
            self.contacts.remove_contact(name)
            self.speak_dialog("contact_deleted", {"contact": name})

    def speak_and_hang(self, speech):
        self._wait_until_call_established()
        self.sip.mute_mic()
        self.sip.speak(speech)
        self.hang_call()

    def handle_call_established(self):
        self.handle_gui_state("Connected")
        if self.cb is not None:
            self.cb()
            self.cb = None

    def handle_login_success(self):
        pass
        #self.speak_dialog("sip_login_success")

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
        if number.startswith("sip:"):
            number = number[4:]
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
            self.gui["currentContact"] = contact["name"]
            self.handle_gui_state("Incoming")
            self.speak_dialog("incoming_call", {"contact": contact["name"]},
                              wait=True)
        else:
            self.gui["currentContact"] = "Unknown"
            self.handle_gui_state("Incoming")
            self.speak_dialog("incoming_call_unk", wait=True)
        self.intercepting_utterances = True

    def handle_call_ended(self, reason):
        self.handle_gui_state("Hang")
        self.log.info("Call ended")
        self.log.debug("Reason: " + reason)
        self.intercepting_utterances = False
        self.speak_dialog("call_ended", {"reason": reason})
        self.on_hold = False
        self.muted = False

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
                    self.speak_and_hang(speech)
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
            self.gui["currentContact"] = name
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
            self.speak_and_hang(utterance)

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
        self.gui["contactListModel"] = self.contacts.list_contacts()
        self.handle_gui_state("Contacts")
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

    @intent_file_handler("call_status.intent")
    def handle_status(self, message):
        if self.sip is not None:
            self.speak_dialog("call_status", {"status": self.sip.call_status})
        else:
            self.speak_dialog("sip_not_running")

    # sipxcom intents
    @intent_file_handler("sipxcom_sync.intent")
    def handle_syncs(self, message):
        self.sipxcom_sync()

    def sipxcom_sync(self):
        try:
            sipxcom = SipXCom(self.settings["sipxcom_user"],
                              self.settings["sipxcom_password"],
                              self.settings["sipxcom_gateway"])
            if sipxcom.check_auth():
                contacts = sipxcom.get_contacts(True)
                for c in contacts:
                    self.add_new_contact(c["name"], c["url"], prompt=True)
            else:
                self.speak_dialog("sipxcom_badcreds")
        except Exception as e:
            self.speak_dialog("sipxcom_sync_error")
            self.log.exception(e)

    # converse
    def converse_keepalive(self):
        while True:
            if self.settings["intercept_allowed"]:
                # avoid converse timed_out
                self.make_active()
            time.sleep(60)

    def converse(self, utterances, lang="en-us"):
        if self.settings["intercept_allowed"] and utterances is not None:
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

    # Handle GUI States Centerally
    def handle_gui_state(self, state):
        self.gui["call_muted"] = False
        if state == "Hang":
            self.gui["pageState"] = "Disconnected"
            self.gui.show_page("voipLoader.qml", override_idle=True)
            time.sleep(5)
            self.gui["currentContact"] = "Unknown"
            self.gui.clear()
            self.enclosure.display_manager.remove_active()
            self.bus.emit(Message("mycroft.mark2.reset_idle"))
        elif state == "Clear":
            self.gui["currentContact"] = "Unknown"
            self.gui.clear()
            self.enclosure.display_manager.remove_active()
            self.bus.emit(Message("mycroft.mark2.reset_idle"))
        else:
            self.gui["pageState"] = state
            self.gui.show_page("voipLoader.qml", override_idle=True)
            
    # Handle GUI Show Home
    @intent_file_handler("show_home.intent")
    def show_homescreen(self):
        self.handle_gui_state("Homescreen")
        
    # Handle Config From GUI
    def handle_config_from_gui(self, message):
        if message.data["type"] is not "SipXCom":
            self.settings["user"] = message.data["username"]
            self.settings["gateway"] = message.data["gateway"]
            self.settings["password"] = message.data["password"]
        else:
            self.settings["sipxcom_user"] = message.data["username"]
            self.settings["sipxcom_gateway"] = message.data["gateway"]
            self.settings["sipxcom_password"] = message.data["password"]
        self.sip.quit()
        self.sip = None
        self.handle_restart({})
        
    # Handle Contact Calling From GUI
    def handle_call_contact_from_gui(self, message):
        if self.sip is not None:
            self.handle_gui_state("Outgoing")
            self.handle_call_contact(message)
        else:
            self.handle_call_failure_gui()
            
    # Handle Failure
    def handle_call_failure_gui(self):
        self.handle_gui_state("Failed")
        sleep(3)
        self.handle_gui_state("Clear")
            
# SIPXCOM integration

def etree2dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree2dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def xml2dict(xml_string):
    def _clean_dict(d):
        cleaned = {}
        for k in d:
            if isinstance(d[k], dict):
                d[k] = _clean_dict(d[k])

            if isinstance(d[k], list):
                for idx, entry in enumerate(d[k]):
                    if isinstance(entry, dict):
                        d[k][idx] = _clean_dict(entry)

            n = k
            if k.startswith("@") or k.startswith("#"):
                n = k[1:]
            cleaned[n] = d[k]
        return cleaned

    try:
        xml_string = xml_string.replace('xmlns="http://www.w3.org/1999/xhtml"',
                                        "")
        e = ET.XML(xml_string)
        d = etree2dict(e)
        return _clean_dict(d)
    except:
        return {}


class SipXCom:
    def __init__(self, user, pswd, gateway):
        self.gateway = gateway.replace("https://", "").replace("http://", "")
        self.base_url = "https://{gateway}/sipxconfig/rest/my/". \
            format(gateway=self.gateway)

        self.user = user
        self.pswd = pswd

    def check_auth(self):
        url = self.base_url + "speeddial"
        data = requests.get(url, verify=False,
                            auth=HTTPBasicAuth(self.user, self.pswd))
        return data.status_code == 200

    def speeddial(self):
        url = self.base_url + "speeddial"
        data = requests.get(url, verify=False,
                            auth=HTTPBasicAuth(self.user, self.pswd)).json()
        return data

    def phonebook(self):
        url = self.base_url + "phonebook"
        data = requests.get(url, verify=False,
                            auth=HTTPBasicAuth(self.user, self.pswd))
        data = xml2dict(data.text)
        return data

    def speeddial_contacts(self):
        data = self.speeddial()
        contacts = [{"name": a["label"].replace("_", " ").replace("-", " ").strip(),
                     "url": a["number".strip()]} for a in
                    data["buttons"]]
        return contacts

    def phonebook_contacts(self):
        data = self.phonebook()
        contacts = [
            {"name": a["contact-information"]["imDisplayName"].replace("_", " ").replace("-", " ").strip(),
             "url": a["number"].strip() + "@" + self.gateway} for a in
            data["phonebook"]["entry"]]
        return contacts

    def get_contacts(self, dedup=True):
        if dedup:
            contacts = self.speeddial_contacts()
            addr_list = [c["name"] for c in contacts]
            for c in self.phonebook_contacts():
                if c["name"] not in addr_list:
                    contacts.append(c)
        else:
            contacts = self.speeddial_contacts() + self.phonebook_contacts()
        return contacts


def create_skill():
    return SIPSkill()
