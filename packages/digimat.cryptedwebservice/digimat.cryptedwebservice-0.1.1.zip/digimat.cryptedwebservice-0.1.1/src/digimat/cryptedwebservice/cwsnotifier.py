from cryptedwebservice import CryptedWebservice

class CWSNotifier(CryptedWebservice):
    def __init__(self, wsurl, wsid, wskey):
        super(CWSNotifier, self).__init__(wsurl, wsid, wskey)

    def pushover(self, recipient, title, message, priority=0, sound=None):
        try:
            data="""<root>
                    <recipient>%s</recipient>
                    <title>%s</title>
                    <message>%s</message>
                    <priority>%d</priority>
                    <sound>%s</sound>
                    </root>""" % (recipient,
                                  title,
                                  message,
                                  int(priority),
                                  sound)
            return self.doAndCheckSuccess('pushover', data)
        except:
            pass

    def whatsapp(self, recipient, message):
        try:
            data="""<root>
                    <recipient>%s</recipient>
                    <message>%s</message>
                    </root>""" % (recipient, message)
            return self.doAndCheckSuccess('whatsapp', data)
        except:
            pass
