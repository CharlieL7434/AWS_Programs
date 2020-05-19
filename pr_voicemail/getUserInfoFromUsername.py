import config


class SlackMessage(object):
    def __init__(self, text=None, subject=None, channel=config.DEFAULT_CHANNEL_NAME, warning=None):
        self.text = text
        self.subject = subject
        self.channel = channel
        self.warning = warning

    def __setattr__(self, name, val):
        self.__dict__[name] = val

    @classmethod
    def from_json(cls, json_obj):
        m = cls()
        for key in json_obj.keys():
            setattr(m, key, json_obj[key])
        return m

    def __str__(self):
        myMessage = f'*{self.subject}*\n{self.text}'

        if self.warning is not None :
            myMessage += f'Warning: {self.warning}'

        return myMessage
