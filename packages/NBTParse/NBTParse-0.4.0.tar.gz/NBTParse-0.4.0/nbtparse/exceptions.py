class MalformedNBTError(Exception):
    """Base class of all exceptions caused by malformed or invalid NBT.

    NBT does not provide any easy method to recover from this sort of error.

    The source file's offset pointer is not reset, because it might not be
    possible to do so.  If you want to seek back to the beginning, do so
    manually.
    """
    pass


class NoSuchTagTypeError(MalformedNBTError):
    """Raised if an unrecognized tag type is used."""
    pass


class IncompleteSequenceError(MalformedNBTError):
    """Raised if a sequence is incomplete (i.e. we hit EOF too early)."""
    pass


class ParserError(Exception):
    """Exception raised by :func:`.minecraft.ids.read_config`.

    Raised if the config file is ill-formed.

    """
    pass


class ConcurrentError(Exception):
    """Exception raised when concurrent operations conflict.

    NBTParse is generally not thread-safe.  These exceptions are usually only
    raised in response to process-level concurrency (e.g. while interacting
    with the filesystem).  Thread safety violations may cause this exception
    to be raised, but you should not depend on this behavior.

    """
    pass


class DuplicateIDError(Exception):
    """Exception raised when an entity ID is registered more than once."""
    pass


class ClassWarning(UserWarning):
    """Warning issued when a class definition is dubious."""
    pass


class SliceWarning(UserWarning):
    """Warning issued when using dubious slicing syntax."""
    pass


class ValueWarning(UserWarning):
    """Warning issued when passing dubious values."""
    pass

class UnclosedWarning(UserWarning):
    """Warning issued when an object is not closed properly.

    This is usually issued by a finalizer, so it's probably a bad idea to
    convert these warnings into exceptions.  Exceptions raised in a finalizer
    will just be turned back into warnings anyway.

    """
    pass
