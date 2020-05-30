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

## Contacts

You can add contacts under home.mycroft.ai (no privacy!) or manually edit the json file at ```~/.baresip/mycroft_sip```

NOTE: contacts are WIP, basically a name mycroft can understand mapped to a sip address

    TODO guide for both approaches

## Calling

X is assumed to be a previously configured contact

- call X
- call X and say Y
- accept call
- accept call and say Y
- hang up
- reject call

There also a few admin/debug intents, you should never need to use these

- restart sip
- sip login