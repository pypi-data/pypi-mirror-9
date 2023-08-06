import asyncio

class Message(object):

    def __init__(self, message, payload={}, response=False):
        if not isinstance(message, str):
            raise TypeError('Message must be a string.')
        if not len(message):
            raise ValueError('Message must not be a zero length string')
        if not isinstance(payload, dict):
            raise TypeError('Message payload must be a dict.')

        self.message = message
        self.payload = payload
        if response:
            self.response = asyncio.Future()
        else:
            self.response = None
        self.expects_response = response

    def __repr__(self):
        return 'Message: {0}\nPayload: {1}'.format(self.message, self.payload)

# Special type of message that expects a response
class QueryMessage(Message):

    def __init__(self, message, payload={}):
        super().__init__(message, payload, True)

# Special type of message that tells actors to quit processing their inbox
class ShutdownMessage(Message):

    def __init__(self):
        super().__init__('__SHUTDOWN__')