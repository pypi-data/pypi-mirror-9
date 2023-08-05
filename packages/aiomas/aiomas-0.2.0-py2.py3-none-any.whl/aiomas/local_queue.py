


@asyncio.coroutine
def create_localqueue_connection(protocol_factory, local_queue, **kwds):
    p = protocol_factory()
    t = LocalQueueTransport()
    p.set_transport(t)
    return (t, p)


@asyncio.coroutine
def create_localqueue_server(protocol_factory, local_queue, **kwds):
    p = protocol_factory()
    t = LocalQueueTransport()
    p.set_transport(t)
    return addr


class LocalQueueTransport(asyncio.Transport):
    def __init__(self, queue, protocol):
        self._queue = queue
        self._protocol = protocol
        self._pause_reading = False
        self._task_recv = asyncio.async(self._recv())

    @asyncio.coroutine
    def _recv(self):
        while self._queue is not None:
            data = yield from self._queue.get()
            self._protocol.data_received(data)

    def close(self):
        """Close the transport.

        Buffered data will be flushed asynchronously.  No more data
        will be received.  After all buffered data is flushed, the
        protocol's connection_lost() method will (eventually) called
        with None as its argument.
        """
        self._task_recv.cancel()
        self._queue = None

    def pause_reading(self):
        """Pause the receiving end.

        No data will be passed to the protocol's data_received()
        method until resume_reading() is called.
        """
        self._pause_reading = True

    def resume_reading(self):
        """Resume the receiving end.

        Data received will once again be passed to the protocol's
        data_received() method.
        """
        self._pause_reading = False

    def set_write_buffer_limits(self, high=None, low=None):
        """Set the high- and low-water limits for write flow control.

        These two values control when to call the protocol's
        pause_writing() and resume_writing() methods.  If specified,
        the low-water limit must be less than or equal to the
        high-water limit.  Neither value can be negative.

        The defaults are implementation-specific.  If only the
        high-water limit is given, the low-water limit defaults to a
        implementation-specific value less than or equal to the
        high-water limit.  Setting high to zero forces low to zero as
        well, and causes pause_writing() to be called whenever the
        buffer becomes non-empty.  Setting low to zero causes
        resume_writing() to be called only once the buffer is empty.
        Use of zero for either limit is generally sub-optimal as it
        reduces opportunities for doing I/O and computation
        concurrently.
        """
        raise NotImplementedError

    def get_write_buffer_size(self):
        """Return the current size of the write buffer."""
        raise NotImplementedError

    def write(self, data):
        """Write some data bytes to the transport.

        This does not block; it buffers the data and arranges for it
        to be sent out asynchronously.
        """
        self._queue.put_nowait()

    def can_write_eof(self):
        """Return True if this transport supports write_eof(), False if not."""
        raise False

    def abort(self):
        """Close the transport immediately.

        Buffered data will be lost.  No more data will be received.
        The protocol's connection_lost() method will (eventually) be
        called with None as its argument.
        """
        self.close()



class LocalQueue:
    pass
