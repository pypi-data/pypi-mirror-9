"""
Exception types used by *aiomas*.

"""


class IncompleteMessage(Exception):
    """Raised when connection drops while receiving a message.

    *bytes_expected* is the number of bytes of the complete message (including
    the header).

    *bytes_received* is the number of bytes actually received.

    *msg_received* are the actual bytes received so far.

    """
    def __init__(self, bytes_expected, bytes_received, msg_received):
        super().__init__(bytes_expected, bytes_received, msg_received)
        self.bytes_expected = bytes_expected
        self.bytes_received = bytes_received
        self.msg_received = msg_received


class RemoteException(Exception):
    """Wraps a traceback of an exception on the other side of a channel.

    *origin* is the remote peername.

    *remote_traceback* is the remote exception's traceback.

    """
    def __init__(self, origin, remote_traceback):
        super().__init__(origin, remote_traceback)
        self.origin = origin
        self.remote_traceback = remote_traceback

    def __str__(self):
        return 'Origin: %s\n%s' % (self.origin, self.remote_traceback)
