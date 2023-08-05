"""Types for the various NBT tags.

Every tag type has a corresponding Pythonic class.  Most of these are
subclasses of various built-in classes with additional NBT encoding and
decoding functionality.  Generally speaking, ``TAG_Foo``'s counterpart will be
called ``FooTag``.  Most tags are immutable and hashable, and use a
values-based definition of equality; this is usually inherited from the
corresponding built-in class.

The tags all inherit from :class:`TagMixin`, an abstract mixin class.
:class:`TagMixin` provides some method implementations and a great deal of
high-level documentation; if a particular tag's documentation is unclear,
consult :class:`TagMixin` as well.

:meth:`TagMixin.decode_named` is also exposed at the module level for
convenience.

This module will also log the encoding and decoding process via
:mod:`logging`; the logger has the same name as the module.  Since encoding
and decoding are generally very low-level processes, nearly everything is
logged at the ``DEBUG`` level; some irregularities when decoding are logged at
``WARNING``, and irregularities while encoding will instead generate ordinary
warnings (i.e.  :func:`warnings.warn`).  See the :mod:`logging` documentation
for instructions on how to access this data or ignore it.

"""

import abc
import struct
import warnings
from functools import total_ordering
import io
import logging

from . import ids
from .. import exceptions


logger = logging.getLogger(__name__)


class TagMixin(metaclass=abc.ABCMeta):
    """Abstract mixin class for tags.

    All NBT tags inherit from TagMixin.
    """

    __slots__ = ()

    @abc.abstractmethod
    def encode_payload(self, output: io.BufferedIOBase,
                       errors: str='strict') -> int:
        """Encode the payload of this tag.

        Writes to output and returns number of bytes written.  Output should
        provide a :meth:`write` method but is otherwise unconstrained in
        type.

        If a string needs to be encoded, pass :obj:`errors` to the Unicode
        encoder; ignored on tags which don't need to encode strings.

        If a value is out of range, an :exc:`OverflowError` may result.

        .. note::

           :meth:`output.write` must perform any buffering that may be
           necessary to the underlying I/O; it should write its entire
           argument, unless something has gone wrong.
           :class:`io.BufferedIOBase` and its subclasses satisfy this
           requirement when in non-interactive mode, but may raise
           :exc:`BlockingIOError` if in non-blocking mode.  If you want to use
           non-blocking I/O here, look into event-driven frameworks; many
           provide non-blocking file and socket implementations with
           buffer-like behavior.

        """
        raise NotImplementedError('TagMixin does not implement '
                                  'encode_payload.')

    @property
    @abc.abstractmethod
    def tag_id(self) -> int:
        """The ID of this tag (e.g. 1 for a TAG_Byte)."""
        raise NotImplementedError("TagMixin does not implement tag_id.")

    def encode_named(self, name: str, output: io.BufferedIOBase,
                     errors: str='strict') -> int:
        """Encode this tag with a name (e.g. in a ``TAG_Compound``).

        Writes to output and returns bytes written; see
        :meth:`encode_payload` for some caveats related to this.

        Name should be a :class:`unicode` object, not a string.

        :obj:`errors` will be used in encoding the name and payload of this
        tag.

        """
        total_length = ByteTag(self.tag_id).encode_payload(output)
        total_length += StringTag(name).encode_payload(output, errors)
        total_length += self.encode_payload(output, errors)
        logger.debug("Encoded named tag '%s' to output: %i bytes.",
                     name, total_length)
        return total_length

    @classmethod
    @abc.abstractmethod
    def decode_payload(cls, input: io.BufferedIOBase, errors: str='strict'):
        """Decode a payload from :obj:`input`.

        Reads from :obj:`input` and returns an instance of this tag.
        :obj:`input` should provide a :meth:`read` method but is otherwise
        unconstrained in type.

        If a string needs to be decoded, pass :obj:`errors` to the Unicode
        decoder; ignored on tags which don't need to encode strings.

        .. note::

           :meth:`input.read` must perform any buffering that may be necessary
           to the underlying I/O; if it returns less data than was requested,
           that will be interpreted as EOF.  :class:`io.BufferedIOBase` and
           its subclasses satisfy this requirement when in non-interactive
           mode, but may raise :exc:`BlockingIOError` if in non-blocking mode.
           If you want to use non-blocking I/O here, look into event-driven
           frameworks; many provide non-blocking file and socket
           implementations with buffer-like behavior.

        """
        raise NotImplementedError('TagMixin does not implement '
                                  'decode_payload.')

    @classmethod
    def decode_named(cls, input: io.BufferedIOBase, errors: str='strict'):
        """Decode a named tag from input and returns (name, tag).

        Reads from input; see :meth:`decode_payload` for some caveats related
        to this.

        Errors will be passed to the Unicode decoder when decoding the name
        and payload.

        """
        logger.debug("Decoding named tag...")
        tag_id = ByteTag.decode_payload(input, errors)
        if tag_id == ids.TAG_End:  # TAG_End has no name and no payload
            result = EndTag()  # XXX: Special cases are ugly.
            logger.debug("Decoded tag %s.", repr(result))
            return (None, result)
        name = StringTag.decode_payload(input, errors)
        tag = decode_payload(input, tag_id, errors)
        logger.debug("Decoded tag named %s.", name)
        return (name, tag)


def _decode_payload_closure(formatstr, length):
    def decode_payload(cls, input: io.BufferedIOBase,
                       errors: str='strict') -> int:
        """Decode a fixed-width value from input.

        Value is {} bytes wide.

        """
        raw = input.read(length)
        if len(raw) < length:
            raise exceptions.IncompleteSequenceError('Needed {} bytes, '
                                                     'got {}.'
                                                     .format(length,
                                                             len(raw)))
        (value,) = struct.unpack(formatstr, raw)
        result = cls(value)
        logger.debug("Decoded fixed-width tag: %r.", result)
        return result
    decode_payload.__doc__ = decode_payload.__doc__.format(length)
    return decode_payload


def _encode_payload_closure(formatstr):
    def encode_payload(self, output: io.BufferedIOBase, errors='strict'):
        """Encode a fixed-width value to output.

        If the value is too large to fit into the appropriate representation,
        an :exc:`OverflowError` will result.

        """
        try:
            raw = struct.pack(formatstr, self)
        except struct.error:
            raise OverflowError("%d is too far from zero to encode.", self)
        output.write(raw)
        total_length = len(raw)
        logger.debug("Encoded %r: %i bytes.", self, total_length)
        return total_length
    return encode_payload


@total_ordering
class EndTag(TagMixin):
    """Represents a ``TAG_End``.

    :class:`EndTag`\ s always compare equal to one another, are immutable and
    hashable, and are considered :obj:`False` by :func:`bool`.  Subclassing it
    is probably not a great idea.

    For all practical purposes, you can think of :func:`EndTag` as the tag
    equivalent of :obj:`None`.

    You probably won't need this very often; TAG_End mostly only shows up as
    the terminating sentinel value for ``TAG_Compound``, and
    :class:`CompoundTag` handles that automatically.  It's here if you need
    it, though.

    """

    __slots__ = ()

    def __repr__(self):
        return "EndTag()"

    def __hash__(self):
        return hash((None, type(self)))  # Always the same value

    def __eq__(self, other):
        return type(other) is type(self)  # All EndTags are equal

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if self == other:
            return False
        else:
            return NotImplemented

    def __bool__(self):
        return False

    def encode_payload(self, output: io.BufferedIOBase,
                       errors: str='strict') -> int:
        """Does nothing, since ``TAG_End`` has no payload."""
        return 0

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`.ids.TAG_End`."""
        return ids.TAG_End

    def encode_named(self, name: str, output: io.BufferedIOBase,
                     errors: str='strict') -> int:
        """Writes a single null byte to :obj:`output`."""
        output.write(b'\x00')
        return 1

    @classmethod
    def decode_payload(cls, input: io.BufferedIOBase, errors: str='strict'):
        """Returns an :class:`EndTag`

        Does not interact with :obj:`input` at all.

        """
        return cls()


class ByteTag(TagMixin, int):
    """Represents a ``TAG_Byte``.

    Derives from :class:`int`, and can be used anywhere an :class:`int` is
    valid.

    """

    __slots__ = ()

    def __repr__(self):
        return "ByteTag({})".format(super().__repr__())

    def __str__(self):
        return super().__repr__()
    encode_payload = _encode_payload_closure(">b")

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`ids.TAG_Byte`."""
        return ids.TAG_Byte
    decode_payload = _decode_payload_closure(">b", 1)
    decode_payload = classmethod(decode_payload)


class ShortTag(TagMixin, int):
    """Represents a ``TAG_Short``.

    Derives from :class:`int`, and can be used anywhere an :class:`int` is
    valid.

    """

    __slots__ = ()

    def __repr__(self):
        return "ShortTag({})".format(super().__repr__())

    def __str__(self):
        return super().__repr__()
    encode_payload = _encode_payload_closure(">h")

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`.ids.TAG_Short`."""
        return ids.TAG_Short
    decode_payload = _decode_payload_closure(">h", 2)
    decode_payload = classmethod(decode_payload)


class IntTag(TagMixin, int):
    """Represents a ``TAG_Int``.

    Derives from :class:`int`, and can be used anywhere an :class:`int` is
    valid.

    """

    __slots__ = ()

    def __repr__(self):
        return "IntTag({})".format(super().__repr__())

    def __str__(self):
        return super().__repr__()
    encode_payload = _encode_payload_closure(">i")

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`.ids.TAG_Int`."""
        return ids.TAG_Int
    decode_payload = _decode_payload_closure(">i", 4)
    decode_payload = classmethod(decode_payload)


class LongTag(TagMixin, int):
    """Represents a ``TAG_Long``.

    Derives from :class:`long`, and can be used anywhere a :class:`long` is
    valid.

    """

    __slots__ = ()

    def __repr__(self):
        return "LongTag({})".format(super().__repr__())

    def __str__(self):
        return super().__repr__()
    encode_payload = _encode_payload_closure(">q")

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`.ids.TAG_Long`."""
        return ids.TAG_Long
    decode_payload = _decode_payload_closure(">q", 8)
    decode_payload = classmethod(decode_payload)


class FloatTag(TagMixin, float):
    """Represents a ``TAG_Float``.

    Derives from :class:`float`, and can be used anywhere a :class:`float` is
    valid.

    """

    __slots__ = ()

    def __repr__(self):
        return "FloatTag({})".format(super().__repr__())

    def __str__(self):
        return super().__repr__()

    encode_payload = _encode_payload_closure(">f")

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`.ids.TAG_Float`."""
        return ids.TAG_Float
    decode_payload = _decode_payload_closure(">f", 4)
    decode_payload = classmethod(decode_payload)


class DoubleTag(TagMixin, float):
    """Represents a ``TAG_Double``.

    Derives from :class:`float`, and can be used anywhere a :class:`float` is
    valid.

    """

    __slots__ = ()

    def __repr__(self):
        return "DoubleTag({})".format(super().__repr__())

    def __str__(self):
        return super().__repr__()
    encode_payload = _encode_payload_closure(">d")

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`.ids.TAG_Double`."""
        return ids.TAG_Double
    decode_payload = _decode_payload_closure(">d", 8)
    decode_payload = classmethod(decode_payload)


class ByteArrayTag(TagMixin, bytes):
    """Represents a ``TAG_Byte_Array``.

    Derives from :class:`bytes`, and can be used anywhere that :class:`bytes`
    would be valid.

    Note that this is generally not used to represent text because it lacks
    encoding information; see :class:`StringTag` for that.

    """

    __slots__ = ()

    def __repr__(self):
        return "ByteArrayTag({})".format(super().__repr__())

    def __str__(self):
        return super().__str__()

    def encode_payload(self, output: io.BufferedIOBase,
                       errors: str='strict') -> int:
        """Writes this tag as a sequence of raw bytes to output.

        Returns the total number of bytes written, including the length.

        """
        logger.debug("Encoding TAG_Byte_Array: len = %i.", len(self))
        total_length = IntTag(len(self)).encode_payload(output, errors)
        total_length += len(self)
        output.write(self)
        logger.debug("Encoded TAG_Byte_Array: %i bytes.", total_length)
        return total_length

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`.ids.TAG_Byte_Array`."""
        return ids.TAG_Byte_Array

    @classmethod
    def decode_payload(cls, input: io.BufferedIOBase, errors: str='strict'):
        """Read a ``TAG_Byte_Array`` payload into a new :class:`ByteArrayTag`.

        """
        logger.debug("Decoding TAG_Byte_Array...")
        array_len = IntTag.decode_payload(input, errors)
        raw = input.read(array_len)
        if len(raw) < array_len:
            raise exceptions.IncompleteSequenceError("Expected {} bytes, "
                                                        "got {}"
                                                        .format(len(raw),
                                                                array_len))
        result = cls(raw)
        logger.debug("Decoded TAG_Byte_Array: len = %i.", len(result))
        return result


class StringTag(TagMixin, str):
    """Represents a ``TAG_String``.

    Derives from :class:`str` and can be used anywhere that :class:`str` is
    valid.

    """

    __slots__ = ()

    def __repr__(self):
        return "StringTag({})".format(super().__repr__())

    def __str__(self):
        return super().__str__()

    def encode_payload(self, output: io.BufferedIOBase,
                       errors: str='strict') -> int:
        """Writes this tag as UTF-8 to output.

        Returns total bytes written, including length.

        Errors is passed to the Unicode encoder.  The default value of
        ``'strict'`` will cause any problems (e.g. invalid surrogates) to
        raise a :exc:`UnicodeError`.

        """
        logger.debug("Encoding TAG_String: %r.", self)
        raw = self.encode('utf_8', errors)
        total_length = ShortTag(len(raw)).encode_payload(output, errors)
        total_length += len(raw)
        output.write(raw)
        logger.debug("Encoded TAG_String: %i bytes.", total_length)
        return total_length

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`.ids.TAG_String`."""
        return ids.TAG_String

    @classmethod
    def decode_payload(cls, input: io.BufferedIOBase, errors: str='strict'):
        """Reads a TAG_String payload into a new StringTag.

        TAG_String is always in UTF-8.

        Errors is passed to the Unicode encoder.  The default value of
        'strict' will cause any problems (e.g. invalid UTF-8) to raise a
        :exc:`UnicodeError`.

        """
        logger.debug("Decoding TAG_String...")
        length = ShortTag.decode_payload(input, errors)
        raw = input.read(length)
        if len(raw) < length:
            raise exceptions.IncompleteSequenceError("Expected {} bytes,"
                                                     " got {}"
                                                    .format(len(raw),
                                                            length))
        result = cls(raw, 'utf_8', errors)
        logger.debug("Decoded TAG_String: %r.", result)
        return result


class ListTag(TagMixin, list):
    """Represents a ``TAG_List``.

    Unlike most other tags, this tag is mutable and unhashable.

    :obj:`instance.content_id<content_id>` identifies the type of the tags
    listed in this tag.  During initialization, ListTag will attempt to guess
    content_id if it is not provided.  If the list is empty, it defaults to
    None and the list will not be encodable.

    """

    __slots__ = ('_content_id',)

    def __init__(self, iterable=None, content_id=None):
        if iterable is None:
            self._content_id = content_id
            super().__init__()
            return
        super().__init__(iterable)
        for tag in self:
            if content_id is None:
                content_id = tag.tag_id
            elif tag.tag_id != content_id:
                raise TypeError("{} has id {}, not {}.".format(repr(tag),
                                                               tag.tag_id,
                                                               content_id))
        self._content_id = content_id  # Bypass property since we just checked

    @property
    def content_id(self) -> int:
        """Identifies the tag id of the tags listed in this ``TAG_List``.

        Starts at :obj:`None` if the list was initially empty and a content_id
        was not provided.  While this is :obj:`None`, the tag cannot be
        encoded.

        """
        return self._content_id

    @content_id.setter
    def content_id(self, value):
        for tag in self:
            if tag.tag_id != value:
                raise TypeError("{} has id {}, not {}.".format(repr(tag),
                                                               tag.tag_id,
                                                               value))
        self._content_id = value

    def __repr__(self):
        return 'ListTag({}, {})'.format(super().__repr__(),
                                        repr(self.content_id))

    def __str__(self):
        return super().__str__()

    def __eq__(self, other):
        return (super().__eq__(other) and
                hasattr(other, "content_id") and
                self.content_id == other.content_id)

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if super().__lt__(other):
            return True
        elif super().__eq__(other):
            if hasattr(other, "content_id"):
                return self.content_id < other.content_id
            else:
                return NotImplemented
        else:
            return False
    # functools.total_ordering won't override list.__gt__ etc.
    # so do it by hand:

    def __gt__(self, other):
        return not self == other and not self < other

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other

    def encode_payload(self, output: io.BufferedIOBase,
                       errors: str='strict') -> int:
        """Encodes a series of tag payloads to :obj:`output`.

        Returns the total number of bytes written, including metadata.

        """
        logger.debug("Encoding TAG_List: %i items.", len(self))
        if self.content_id is None:
            raise ValueError("No content_id specified.")
        self.content_id = ByteTag(self.content_id)
        total_length = self.content_id.encode_payload(output, errors)
        total_length += IntTag(len(self)).encode_payload(output, errors)
        for tag in self:
            if tag.tag_id != self.content_id:
                raise TypeError("{} has id {}, not {}."
                                .format(repr(tag), tag.tag_id,
                                        self.content_id))
            total_length += tag.encode_payload(output, errors)
        logger.debug("Encoded TAG_List: %i bytes.", total_length)
        return total_length

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`.ids.TAG_List`."""
        return ids.TAG_List

    @classmethod
    def decode_payload(cls, input: io.BufferedIOBase, errors: str='strict'):
        """Decode a list of tags."""
        logger.debug("Decoding TAG_List...")
        content_id = ByteTag.decode_payload(input, errors)
        length = IntTag.decode_payload(input, errors)
        result = cls(content_id=content_id)
        for _ in range(length):
            next_item = decode_payload(input, content_id, errors)
            result.append(next_item)
        logger.debug("Decoded TAG_List: %i items.", len(result))
        return result


class CompoundTag(TagMixin, dict):
    """Represents a ``TAG_Compound``.

    Unlike most other tags, this tag is mutable and unhashable.

    Derives from :class:`dict` and may be used in place of one.

    Keys are names, values are tags.

    The terminating ``TAG_End`` is handled automatically; you do not need to
    worry about it.

    This implementation does not preserve the order of the tags; this is
    explicitly permitted under the NBT standard.

    """

    __slots__ = ()

    def __repr__(self):
        return 'CompoundTag({})'.format(super().__repr__())

    def __str__(self):
        return super().__str__()

    def encode_payload(self, output: io.BufferedIOBase,
                       errors: str='strict') -> int:
        """Encodes contents as a series of named tags.

        Tags are fully formed, including ids and names.

        Errors is passed to the Unicode encoder for encoding names, and to the
        individual tag encoders.

        """
        logger.debug("Encoding TAG_Compound: %i entries.", len(self))
        total_length = 0
        for name, tag in self.items():
            if tag == EndTag():
                warnings.warn("Skipping EndTag() in {!r}".format(self),
                              category=exceptions.ValueWarning,
                              stacklevel=2)
                continue
            total_length += tag.encode_named(name, output, errors)
        total_length += EndTag().encode_named(None, output, errors)
        logger.debug("Encoded TAG_Compound: %i bytes.", total_length)
        return total_length

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`.ids.TAG_Compound`."""
        return ids.TAG_Compound

    @classmethod
    def decode_payload(cls, input: io.BufferedIOBase, errors: str='strict'):
        """Decodes a series of named tags into a new :class:`CompoundTag`."""
        logger.debug("Decoding TAG_Compound...")
        result = cls()
        sentinel = EndTag()
        new_name, new_tag = cls.decode_named(input, errors)
        while new_tag != sentinel:
            if new_name in result:
                logger.warn("Found duplicate %s in TAG_Compound, "
                            "ignoring.", new_name)
                continue
            result[new_name] = new_tag
            new_name, new_tag = cls.decode_named(input, errors)
        logger.debug("Decoded TAG_Compound: %i entries.", len(result))
        return result


class IntArrayTag(TagMixin, list):
    """Represents a ``TAG_Int_Array``.

    Unlike most other tags, this tag is mutable and unhashable.

    Derives from :class:`list` and may be used in place of one.

    """

    __slots__ = ()

    def __repr__(self):
        return 'IntArrayTag({})'.format(super().__repr__())

    def __str__(self):
        return super().__str__()

    def encode_payload(self, output, errors='strict'):
        """Encodes contents as a series of integers."""
        logger.debug("Encoding TAG_Int_Array: %i integers.", len(self))
        cooked = [IntTag(x) for x in self]
        length = IntTag(len(cooked))
        total_length = length.encode_payload(output, errors)
        for tag in cooked:
            total_length += tag.encode_payload(output, errors)
        logger.debug("Encoded TAG_Int_Array: %i bytes.", total_length)
        return total_length

    @property
    def tag_id(self) -> int:
        """Equal to :obj:`.ids.TAG_Int_Array`."""
        return ids.TAG_Int_Array

    @classmethod
    def decode_payload(cls, input: io.BufferedIOBase, errors: str='strict'):
        """Decodes a series of integers into a new :class:`IntArrayTag`."""
        logger.debug("Decoding TAG_Int_Array...")
        result = cls()
        length = IntTag.decode_payload(input, errors)
        for _ in range(length):
            item = IntTag.decode_payload(input, errors)
            result.append(item)
        logger.debug("Decoded TAG_Int_Array: %i integers.", len(result))
        return result

#: Same as :meth:`TagMixin.decode_named`
decode_named = TagMixin.decode_named


def decode_payload(input, tag_id: int, errors: str='strict') -> TagMixin:
    """Decode a payload with tag ID :obj:`tag_id`.

    Helper function to look up the appropriate class and call its
    :meth:`~TagMixin.decode_payload` method.

    """
    classes = {
        ids.TAG_End: EndTag,
        ids.TAG_Byte: ByteTag,
        ids.TAG_Short: ShortTag,
        ids.TAG_Int: IntTag,
        ids.TAG_Long: LongTag,
        ids.TAG_Float: FloatTag,
        ids.TAG_Double: DoubleTag,
        ids.TAG_Byte_Array: ByteArrayTag,
        ids.TAG_String: StringTag,
        ids.TAG_List: ListTag,
        ids.TAG_Compound: CompoundTag,
        ids.TAG_Int_Array: IntArrayTag,
        }
    klass = classes[tag_id]
    return klass.decode_payload(input, errors)
