"""The exceptions module contains special exceptions to be raised by
this library.
"""

class TimeoutError(Exception):
    """Raised when a read operation exceeded its specified time limit."""
    pass

class UnexpectedReplyError(Exception):
    """Raised when a reply was read from an unexpected device."""
    pass
