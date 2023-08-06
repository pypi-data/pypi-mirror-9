# -*- coding: utf-8 -*-
"""
hyper/http20/exceptions
~~~~~~~~~~~~~~~~~~~~~~~

This defines exceptions used in the HTTP/2 portion of hyper.
"""
class SocketError(Exception):
    """
    An error occurred during socket operation.
    """
    pass


class LineTooLongError(Exception):
    """
    An attempt to read a line from a socket failed because no newline was
    found.
    """
    pass


class HTTP20Error(Exception):
    """
    The base class for all of ``hyper``'s HTTP/2-related exceptions.
    """
    pass


class HPACKEncodingError(HTTP20Error):
    """
    An error has been encountered while performing HPACK encoding.
    """
    pass


class HPACKDecodingError(HTTP20Error):
    """
    An error has been encountered while performing HPACK decoding.
    """
    pass


class ConnectionError(HTTP20Error):
    """
    The remote party signalled an error affecting the entire HTTP/2
    connection, and the connection has been closed.
    """
    pass


class ProtocolError(HTTP20Error):
    """
    The remote party violated the HTTP/2 protocol.
    """
    pass


# Create our own ConnectionResetError.
try:  # pragma: no cover
    ConnectionResetError = ConnectionResetError
except NameError:  # pragma: no cover
    class ConnectionResetError(Exception):
        """
        A HTTP/2 connection was unexpectedly reset.
        """
