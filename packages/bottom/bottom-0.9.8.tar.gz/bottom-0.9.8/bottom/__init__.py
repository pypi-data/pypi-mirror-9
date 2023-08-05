""" asyncio-based rfc2812-compliant IRC Client """
import logging
import asyncio
from . import event
from . import pack
from . import unpack
__all__ = ["Client"]
logger = logging.getLogger(__name__)


class Client(event.EventsMixin):
    def __init__(self, host, port, encoding='UTF-8', ssl=True):
        # It's ok that unpack.parameters isn't cached, since it's only
        # called when adding an event handler (which should __usually__
        # only occur during setup)
        super().__init__(unpack.parameters)
        # trigger events on the client
        self.connection = Connection(host, port, self,
                                     encoding=encoding, ssl=ssl)

    def send(self, command, **kwargs):
        '''
        Send a message to the server.

        Examples
        --------
        client.send('nick', nick='weatherbot')
        client.send('privmsg', target='#python', message="Hello, World!")

        '''
        self.connection.send(pack.pack_command(command, **kwargs))

    @asyncio.coroutine
    def connect(self):
        yield from self.connection.connect()

    @asyncio.coroutine
    def disconnect(self):
        yield from self.connection.disconnect()

    @property
    def connected(self):
        return self.connection.connected

    @asyncio.coroutine
    def run(self, loop=None):
        ''' Run the client until it disconnects (without reconnecting) '''
        yield from self.connection.run(loop=loop)

    def on(self, command):
        '''
        Decorate a function to be invoked when a :param:`command` occurs.
        '''
        return super().on(command.upper())


class Connection(object):
    def __init__(self, host, port, events, encoding, ssl):
        self.events = events
        self._connected = False
        self.host, self.port = host, port
        self.reader, self.writer = None, None
        self.encoding = encoding
        self.ssl = ssl

    @asyncio.coroutine
    def connect(self, loop=None):
        if self.connected:
            return
        self.reader, self.writer = yield from asyncio.open_connection(
            self.host, self.port, ssl=self.ssl, loop=loop)
        self._connected = True
        yield from self.events.trigger(
            "CLIENT_CONNECT", host=self.host, port=self.port)

    @asyncio.coroutine
    def disconnect(self):
        if not self.connected:
            return
        self.writer.close()
        self.writer = None
        self.reader = None
        self._connected = False
        yield from self.events.trigger(
            "CLIENT_DISCONNECT", host=self.host, port=self.port)

    @property
    def connected(self):
        return self._connected

    @asyncio.coroutine
    def run(self, loop=None):
        yield from self.connect(loop=loop)
        while self.connected:
            msg = yield from self.read()
            if msg:
                try:
                    event, kwargs = unpack.unpack_command(msg)
                except ValueError:
                    logger.exception(
                        "Couldn't parse line <<<{}>>>".format(msg))
                else:
                    yield from self.events.trigger(event, **kwargs)
            else:
                # Lost connection
                yield from self.disconnect()

    def send(self, msg):
        if self.writer:
            self.writer.write((msg.strip() + '\n').encode(self.encoding))

    @asyncio.coroutine
    def read(self):
        if not self.reader:
            return ''
        try:
            msg = yield from self.reader.readline()
            return msg.decode(self.encoding, 'ignore').strip()
        except EOFError:
            return ''
