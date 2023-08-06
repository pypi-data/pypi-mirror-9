__author__ = 'Andrew Ben'

class Message():
    __messageId = -1
    __subject = ''
    __body = ''
    __sender = ''
    __recipients = []
    __replyOptions = []
    __callbackUrl = ''

    def __init__(self):
        pass


    @property
    def messageId(self):
        return self.__messageId

    @messageId.setter
    def messageId(self, value):
        self.__messageId = value


    @property
    def messageId(self):
        return self.__messageId

    @messageId.setter
    def messageId(self, value):
        self.__messageId = value


    @property
    def subject(self):
        return self.__subject

    @subject.setter
    def subject(self, value):
        self.__subject = value

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, value):
        self.__body = value

    @property
    def sender(self):
        return self.__sender

    @sender.setter
    def sender(self, value):
        self.__sender = value

    @property
    def recipients(self):
        return self.__recipients

    @recipients.setter
    def recipients(self, value):
        self.__recipients = value

    @property
    def replyOptions(self):
        return self.__replyOptions

    @replyOptions.setter
    def replyOptions(self, value):
        self.__replyOptions = value

    @property
    def callBackUrl(self):
        return self.__callbackUrl

    @callBackUrl.setter
    def callBackUrl(self, value):
        self.__callbackUrl = value


