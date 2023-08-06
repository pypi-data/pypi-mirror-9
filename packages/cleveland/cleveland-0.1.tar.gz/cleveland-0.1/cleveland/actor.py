from .message import Message, QueryMessage, ShutdownMessage
import asyncio

class Actor(object):

    def __init__(self, *args, **kwargs):
        self._inbox = asyncio.Queue(maxsize=kwargs.get('max_inbox_size', 0))

        self._setup(*args, **kwargs)
        self._running = False

    def _setup(self, *args, **kwargs):
        # Define _setup in subclasses to do interesting things with arguments
        pass

    @asyncio.coroutine
    def _shutdown(self):
        # Define _shutdown in subclasses to do interesting things after the
        # actor has been told to shut down.
        pass

    @asyncio.coroutine
    def receive(self, message):
        if not isinstance(message, Message):
            raise TypeError('Message must be of type cleveland.message.Message')
        yield from self._inbox.put(message)

    @asyncio.coroutine
    def tell(self, target, message):
        if not isinstance(target, Actor):
            raise TypeError('Target must be of type cleveland.actor.Actor.')
        if not isinstance(message, Message):
            raise TypeError('Message must be of type cleveland.message.Message')
        yield from target.receive(message)

    @asyncio.coroutine
    def ask(self, target, message):
        if not isinstance(message, QueryMessage):
            raise TypeError('Message must of be of type cleveland.message.QueryMessage')
        yield from self.tell(target, message)
        retval = yield from message.response
        return retval

    @asyncio.coroutine
    def run(self):
        self._running = True
        while self._running:
            message = yield from self._inbox.get()
            if isinstance(message, ShutdownMessage):
                self._running = False
                yield from self._shutdown()
            else:
                yield from self._process(message)

    @asyncio.coroutine
    def stop(self):
        yield from self.receive(ShutdownMessage())

    @asyncio.coroutine
    def _process(self, message):
        if message.expects_response:
            message.response.set_result(None)
        else:
            pass
