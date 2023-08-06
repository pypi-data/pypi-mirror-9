from suds.client import Client

__author__ = 'Andrew Ben'

class OnPageHubApi():
    def __init__(self, url, enterpiseName, token):
        self.__url = url
        self.__enterpiseName = enterpiseName
        self.__token = token

        self.__hubApiClient = Client(url)
        self.__hubApiClient.set_options(location=url)


    def __getCredentials(self):
        credentials = self.__hubApiClient.factory.create('Credentials')
        credentials.Token = '%s+%s' % (self.__enterpiseName, self.__token)
        return credentials

    def __createSender(self, senderId):
        sender = self.__hubApiClient.factory.create('Sender')
        senderType = self.__hubApiClient.factory.create('SENDER_TYPE')
        if senderId.find('@') > 0:
            sender.type = senderType.EMAIL
        else:
            sender.type = senderType.PAGER
        sender.ID = senderId

        return sender

    def __createRecipient(self, recipient):
        hubApiRecipient = self.__hubApiClient.factory.create('Recipient')
        hubApiRecipient.id = recipient
        return hubApiRecipient

    def __createMessage(self, messageId, sender, recipients, subject, body, replyOptions, callBackUrl):
        message = self.__hubApiClient.factory.create('Message')

        message.id = messageId

        message.Sender = self.__createSender(senderId=sender)

        message.Subject = subject
        message.Body = body

        listOfRecipients = []
        for recipient in recipients:
            listOfRecipients.append(self.__createRecipient(recipient))
        message.Recipients = {'Recipient': [listOfRecipients]}

        replies = self.__hubApiClient.factory.create('ReplyOptions')
        replies.AllowFreeText = True
        replies.Requested = {'Option': replyOptions}

        message.Reply = replyOptions

        message.CallbackURI = callBackUrl

        return message


    def __prepareMessages(self, messages):
        listOfMessages = []
        for message in messages:
            hubApiMessage = self.__createMessage(
                messageId=message.messageId,
                sender=message.sender,
                recipients=message.recipients,
                subject=message.subject,
                body=message.body,
                replyOptions=message.replyOptions,
                callBackUrl=message.callBackUrl
            )

            listOfMessages.append(hubApiMessage)

        arrayOfMessages = {'Message': listOfMessages}

        return arrayOfMessages

    def sendPage(self, messages):
        arrayOfMessages = self.__prepareMessages(messages)

        return self.__hubApiClient.service.SendMessage(self.__getCredentials(), arrayOfMessages)
