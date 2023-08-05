"""
This module implements and asyncio :class:`asyncio.Protocol` protocol for a
request-reply :class:`Channel`.

"""
__all__ = [
    'REQUEST', 'RESULT', 'EXCEPTION',
    'open_connection', 'start_server',
    'Header', 'Request', 'Channel', 'ChannelProtocol',
]

from asyncio import coroutine
import asyncio
import collections
import itertools
import struct
import traceback

from aiomas.exceptions import RemoteException
import aiomas.codecs


# Message types
REQUEST = 0
RESULT = 1
EXCEPTION = 2

DEFAULT_CODEC = aiomas.codecs.MsgPack

Header = struct.Struct('!L')


@coroutine
def open_connection(addr, *, loop=None, codec=None, **kwds):
    """Return a :class:`Channel` connected to *addr*.

    This is a convenience wrapper for
    :meth:`asyncio.BaseEventLoop.create_connection()` and
    :meth:`asyncio.BaseEventLoop.create_unix_connection`.

    If *addr* is a tuple ``(host, port)``, a TCP connection will be created.
    If *addr* is a string, it should be a path name pointing to the unix domain
    socket to connect to.

    You can optionally provide the event *loop* to use.

    By default, the :class:`~aiomas.codecs.MsgPack` *codec* is used. You
    can override this with any subclass of :class:`aiomas.codecs.Codec`.

    The remaining keyword argumens *kwds* are forwarded to
    :meth:`asyncio.BaseEventLoop.create_connection()` and
    :meth:`asyncio.BaseEventLoop.create_unix_connection` respectively.

    """
    if loop is None:
        loop = asyncio.get_event_loop()

    if not codec:
        codec = DEFAULT_CODEC()

    def factory():
        return ChannelProtocol(codec, loop=loop)

    if type(addr) is tuple:
        t, p = yield from loop.create_connection(factory, *addr, **kwds)
    elif type(addr) is str:
        t, p = yield from loop.create_unix_connection(factory, addr, **kwds)
    else:
        raise ValueError('Unkown address type: %s' % addr)

    return p.channel


@coroutine
def start_server(addr, client_connected_cb, *, loop=None, codec=None, **kwds):
    """Start a server listening on *addr* and call *client_connected_cb*
    for every client connecting to it.

    This function is a convenience wrapper for
    :meth:`asyncio.BaseEventLoop.create_server()` and
    :meth:`asyncio.BaseEventLoop.create_unix_server`.

    If *addr* is a tuple ``(host, port)``, a TCP socket will be created.  If
    *addr* is a string, a unix domain socket at this path will be created.

    The single argument of the callable *client_connected_cb* is a new instance
    of :class:`Channel`.

    You can optionally provide the event *loop* to use.

    By default, the :class:`~aiomas.codecs.MsgPack` *codec* is used. You
    can override this with any subclass of :class:`aiomas.codecs.Codec`.

    The remaining keyword argumens *kwds* are forwarded to
    :meth:`asyncio.BaseEventLoop.create_server()` and
    :meth:`asyncio.BaseEventLoop.create_unix_server` respectively.

    """
    if loop is None:
        loop = asyncio.get_event_loop()

    if not codec:
        codec = DEFAULT_CODEC()

    def factory():
        return ChannelProtocol(codec, client_connected_cb, loop=loop)

    if type(addr) is tuple:
        return (yield from loop.create_server(factory, *addr, **kwds))
    elif type(addr) is str:
        return (yield from loop.create_unix_server(factory, addr, **kwds))
    else:
        raise ValueError('Unkown address type: %s' % addr)


class ChannelProtocol(asyncio.streams.FlowControlMixin, asyncio.Protocol):
    """Asyncio :class:`asyncio.Protocol` which connects the low level transport
    with the high level :class:`Channel` API.

    The *codec* is used to (de)serialize messages.  It should be a sub-class of
    :class:`aiomas.codecs.Codec`.

    Optionally you can also pass a function/coroutine *client_connected_cb*
    that will be executed when a new connection is made (see
    :func:`start_server()`).

    """
    def __init__(self, codec, client_connected_cb=None, *, loop):
        super().__init__(loop=loop)
        self.codec = codec
        self.transport = None
        self.channel = None
        self._client_connected_cb = client_connected_cb
        self._loop = loop
        self._buffer = bytearray()
        self._read_size = None

    def connection_made(self, transport):
        """Create a new :class:`Channel` instance for a new connection.

        Also call the *client_connected_cb* if one was passed to this class.

        """
        self.transport = transport
        self.channel = Channel(self, self.codec, transport, loop=self._loop)

        if self._client_connected_cb is not None:
            res = self._client_connected_cb(self.channel)
            if asyncio.iscoroutine(res):
                self._loop.create_task(res)

    def data_received(self, data):
        """Buffer incomming data until we have a complete message and then
        pass it to :class:`Channel`.

        Messages are fixed length.  The first four bytes (in network byte
        order) encode the length of the following payload.  The payload is
        a triple ``(msg_type, msg_id, content)`` encoded with the specified
        *codec*.

        """
        self._buffer.extend(data)
        while True:
            # We may have more then one message in the buffer,
            # so we loop over the buffer until we got all complete messages.

            if self._read_size is None and len(self._buffer) >= Header.size:
                # Received the complete header of a new message
                self._read_size = Header.unpack_from(self._buffer)[0]
                # TODO: Check for too large messages?
                self._read_size += Header.size

            if self._read_size and len(self._buffer) >= self._read_size:
                # At least one complete message is in the buffer
                data = self._buffer[Header.size:self._read_size]
                self._buffer = self._buffer[self._read_size:]
                self._read_size = None
                msg_type, msg_id, content = self.codec.decode(data)
                try:
                    self.channel._feed_data(msg_type, msg_id, content)
                except RuntimeError as exc:
                    self.channel._set_exception(exc)

            else:
                # No complete message in the buffer. We are done.
                break

    def eof_received(self):
        """Set a :exc:`ConnectionResetError` to the :class:`Channel`."""
        # In previous revisions, an IncompleteMessage error was raised if we
        # already received the beginning of a new message. However, having
        # to types of exceptions raised by this methods makes things more
        # complicated for the user. The benefit of the IncompleteMessage was
        # not big enough.
        self.channel._set_exception(ConnectionResetError())

    def connection_lost(self, exc):
        """Set a :exc:`ConnectionError` to the :class:`Channel` to indicate
        that the connection is closed."""
        if exc is None:  # pragma: no branch
            exc = ConnectionError('Connection closed')
        self.channel._set_exception(exc)
        super().connection_lost(exc)

    @coroutine
    def write(self, content):
        """Serialize *content* and write the result to the transport.

        This method is a coroutine.

        """
        content = self.codec.encode(content)
        content = Header.pack(len(content)) + content
        self.transport.write(content)
        yield from self._drain_helper()


class Request:
    """Represents a request returned by :meth:`Channel.recv()`.  You shoudn't
    instantiate it yourself.

    *content* contains the incoming message.

    *msg_id* is the ID for that message.  It is unique within a channel.

    *protocol* is the channel's :class:`ChannelProtocol` instance that is used
    for writing back the reply.

    To reply to that request you can ``yield from`` :meth:`Request.reply()`
    or :meth:`Request.fail()`.

    """
    def __init__(self, content, message_id, protocol):
        self._content = content
        self._msg_id = message_id
        self._protocol = protocol

    @property
    def content(self):
        """The content of the incoming message."""
        return self._content

    @coroutine
    def reply(self, result):
        """Reply to the request with the provided result."""
        content = (RESULT, self._msg_id, result)
        yield from self._protocol.write(content)

    @coroutine
    def fail(self, exception):
        """Indicate a failure described by the *exception* instance.

        This will raise a :exc:`~aiomas.exceptions.RemoteException` on the
        other side of the channel.

        """
        stacktrace = traceback.format_exception(exception.__class__, exception,
                                                exception.__traceback__)
        content = (EXCEPTION, self._msg_id, ''.join(stacktrace))
        yield from self._protocol.write(content)


class Channel:
    """A Channel represents a request-reply channel between two endpoints. An
    instance of it is returned by :func:`open_connection()` or is passed to the
    callback of :func:`start_server()`.

    *protocol* is an instance of :class:`ChannelProtocol`.

    *transport* is an :class:`asyncio.BaseTransport`.

    *loop* is an instance of an :class:`asyncio.BaseEventLoop`.

    """
    def __init__(self, protocol, codec, transport, loop):
        self._protocol = protocol
        self._codec = codec
        self._transport = transport
        self._loop = loop

        self._message_id = itertools.count()
        self._out_messages = {}  # message_id -> message
        self._in_queue = collections.deque()
        self._waiter = None  # A future.
        self._exception = None

    @property
    def codec(self):
        """The codec used to de-/encode messages send via the channel."""
        return self._codec

    @property
    def transport(self):
        """The transport of this channel (see the `Python documentation
        <https://docs.python.org/3/library/asyncio-protocol.html#transports>`_
        for details).

        """
        return self._transport

    @coroutine
    def send(self, content):
        """Send a request *content* to the other end and wait for a reply.

        This method is a coroutine which will either return a reply or raise
        one of the following exceptions:

        - :exc:`~aiomas.exceptions.RemoteException`: The remote site raised an
          exception during the computation of the result.

        - :exc:`ConnectionError` (or its subclass :exc:`ConnectionResetError`):
          The connection was closed during the request.

        - :exc:`RuntimeError`: If an invalid message type was received.

        .. code-block:: python

           try:
               result = yield from channel.request('ohai')
           except RemoteException as exc:
               print(exc)

        """
        if self._exception is not None:
            raise self._exception

        message_id = next(self._message_id)
        out_message = asyncio.Future(loop=self._loop)
        self._out_messages[message_id] = out_message
        yield from self._protocol.write((REQUEST, message_id, content))
        yield from out_message
        return out_message.result()

    @coroutine
    def recv(self):
        """Wait for an incoming :class:`Request` and return it.

        May raise one of the following exceptions:


        - :exc:`ConnectionError` (or its subclass :exc:`ConnectionResetError`):
          The connection was closed during the request.

        - :exc:`RuntimeError`: If two processes try to read from the same
          channel or if an invalid message type was received.

        """
        if self._exception is not None:
            raise self._exception

        if not self._in_queue:
            if self._waiter is not None:
                raise RuntimeError('recv() called while another coroutine is '
                                   'already waiting for incoming data.')
            self._waiter = asyncio.Future(loop=self._loop)
            try:
                yield from self._waiter
            finally:
                self._waiter = None

        return self._in_queue.popleft()

    def close(self):
        """Close the channel's transport."""
        if self._transport is not None:
            transport = self._transport
            self._transport = None
            return transport.close()

    def get_extra_info(self, name, default=None):
        """Wrapper for :meth:`asyncio.BaseTransport.get_extra_info()`."""
        return self._transport.get_extra_info(name, default)

    def _feed_data(self, msg_type, msg_id, content):
        """Called by :class:`ChannelProtocol` when a new message arrived."""
        if msg_type == REQUEST:
            message = Request(content, msg_id, self._protocol)
            self._in_queue.append(message)

            waiter = self._waiter
            if waiter is not None:
                self._waiter = None
                waiter.set_result(False)

        elif msg_type == RESULT:
            message = self._out_messages.pop(msg_id)
            message.set_result(content)

        elif msg_type == EXCEPTION:
            message = self._out_messages.pop(msg_id)
            origin = self.get_extra_info('peername')
            message.set_exception(RemoteException(origin, content))

        else:
            raise RuntimeError('Invalid message type %d' % msg_type)

    def _set_exception(self, exc):
        """Set an exception as result for all futures managed by the Channel
        in order to stop all coroutines from reading/writing to the socket."""
        self._exception = exc

        # Set exception to wait-recv future
        waiter = self._waiter
        if waiter is not None:
            self._waiter = None
            if not waiter.cancelled():
                waiter.set_exception(exc)

        # Set exception to all message futures which wait for a reply
        for msg in self._out_messages.values():
            if not msg.done():
                msg.set_exception(exc)

        self.close()
