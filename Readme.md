# VOIP skill

Add VOIP capabilities to Mycroft using Baresip

WIP

# Install

```bash
sudo apt-get install baresip
msm install https://github.com/JarbasSkills/skill--voip
```

# Usage

## Credentials

You can either configure credentials in Baresip or use mycroft.home.ai (your credentials will be exposed)

    TODO guide for both approaches

You can get free SIP accounts at https://sip2sip.info or https://www.antisip.com

NOTE: I am NOT recommending a specific SIP provider, I found these with a simple google search and verified they work

note for linphone users, outgoing calls work but incoming calls dont, see https://github.com/BelledonneCommunications/flexisip/issues/95

## Contacts List

You can add contacts under home.mycroft.ai (no privacy!) or manually edit the json file at ```~/.baresip/mycroft_sip```

NOTE: contacts are WIP, basically a name mycroft can understand mapped to a sip address

    TODO guide for both approaches

## Intents

X is assumed to be a previously configured contact

- call X
- call X and say Y
- accept call
- accept call and say Y
- hang up
- reject call
- hold call
- resume call
- mute call
- unmute call
- answer all calls
- answer all calls with Y
- reject all calls
- Do not handle calls automatically
- how many contacts
- List contacts

There also a few admin/debug intents, you should never need to use these

- restart sip
- sip login