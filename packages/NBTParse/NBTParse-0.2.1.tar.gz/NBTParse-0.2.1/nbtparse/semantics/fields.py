"""A field is part of a ``TAG_Compound`` that corresponds to a top-level tag.

It knows how to translate a tag or group of tags into a Pythonic value and
back again, and uses the descriptor protocol to make this translation
seamless.

Typical usage would be something like this::

    class FooFile(NBTFile):
        bar = LongField(u'Bar')

Thereafter, when saving or loading a :class:`FooFile`, the top-level
``TAG_Long`` called ``Bar`` will be accessible under the attribute :obj:`bar`.
The NBT version is still accessible under the ``FooFile.data`` attribute (or
by calling the :meth:`~nbtparse.semantics.nbtobject.NBTObject.to_nbt` method,
which is usually more correct).

Fields are a thin abstraction over the data dict in an :class:`NBTObject`;
modifying the dict may cause Fields to misbehave.

Idea shamelessly stolen from Django, but massively simplified.

"""

import abc
import contextlib
import datetime
import enum
import logging
import struct
import types
import uuid
import warnings

from ..syntax import tags, ids
from .. import exceptions


logger = logging.getLogger(__name__)


NBT_OBJECT = __name__.split('.')
NBT_OBJECT[-1] = 'nbtobject'
NBT_META = list(NBT_OBJECT)
NBT_META.append('NBTMeta')
NBT_META = '.'.join(NBT_META)
NBT_OBJECT.append('NBTObject')
NBT_OBJECT = '.'.join(NBT_OBJECT)


class AbstractField(metaclass=abc.ABCMeta):
    """Root of the Field class hierarchy."""
    def __init__(self, *args, default=None, **kwargs):
        self.default = default
        super().__init__(*args, **kwargs)

    @abc.abstractmethod
    def __get__(self, obj: NBT_OBJECT, owner: NBT_META=None):
        raise NotImplementedError("AbstractField does not implement __get__.")

    @abc.abstractmethod
    def __set__(self, obj: NBT_OBJECT, value: object):
        raise NotImplementedError("AbstractField does not implement __set__.")

    @abc.abstractmethod
    def __delete__(self, obj: NBT_OBJECT):
        raise NotImplementedError('AbstractField does not implement '
                                  '__delete__.')

    def set_default(self, obj: NBT_OBJECT):
        """Reset this field to its "default" value.

        Useful when constructing an NBTObject.

        """
        logger.debug("Resetting %r on %s object to %s.", self,
                     type(obj).__name__, self.default)
        self.__set__(obj, self.default)

    def save(self, obj: NBT_OBJECT):
        """Hook called during :meth:`~.NBTObject.to_nbt`.

        Does nothing by default.

        """
        pass

    def load(self, obj: NBT_OBJECT):
        """Hook called during :meth:`~.NBTObject.from_nbt`.

        Does nothing by default.

        """
        pass


class MutableField(AbstractField):
    """Mutable variant of a field.

    Caches the Pythonic value and holds a reference to it.  Such a value can
    be safely mutated in-place.  Needed for mutable types like lists, as well
    as immutable types whose contents may be mutable, such as tuples.

    The cache_key must be unique within the object.  By convention, it is the
    nbt_name or nbt_names attribute.  It must be hashable but has no other
    restrictions.

    This class must precede any class which overrides :meth:`__get__`,
    :meth:`__set__`, and/or :meth:`__delete__` in the method resolution order.
    In particular, it must precede :class:`MultiField` or
    :class:`SingleField`.  If you do not understand what that means, just make
    sure your code looks like this::

        class FooField(MutableField, SingleField):
            pass

    ...rather than like this::

        class FooField(SingleField, MutableField):
            pass

    Combining with :class:`ReadOnly` is inadvisable and will generate a
    warning.

    """
    def __init__(self, *args, cache_key, **kwargs):
        self._cache_key = cache_key
        super().__init__(*args, **kwargs)

    def save(self, obj: NBT_OBJECT):
        try:
            value = obj._cached[self._cache_key]
        except KeyError:
            super().__delete__(obj)
        else:
            super().__set__(obj, value)

    def load(self, obj: NBT_OBJECT):
        value = super().__get__(obj, type(obj))
        obj._cached[self._cache_key] = value

    def __get__(self, obj: NBT_OBJECT, owner: NBT_META=None) -> object:
        if obj is None:
            return self
        logger.debug('Retrieving mutable value via %r from %s object', self,
                     type(obj).__name__)
        try:
            result = obj._cached[self._cache_key]
        except KeyError:
            logger.debug('Creating new mutable value (via %r, for %s object)',
                         self, type(obj).__name__)
            result = super().__get__(obj, owner)
            obj._cached[self._cache_key] = result
        return result

    def __set__(self, obj: NBT_OBJECT, value: object):
        obj._cached[self._cache_key] = value

    def __delete__(self, obj: NBT_OBJECT):
        super().__delete__(obj)
        obj._cached.pop(self._cache_key, None)


class ReadOnly:
    """Field wrapper which disallows modification.

    :meth:`__set__` and :meth:`__delete__` raise an :exc:`AttributeError`.
    :meth:`__get__` is silently forwarded to the wrapped field.  Other field
    operations are not implemented at all.

    Because :meth:`__get__` forwards all accesses, including class-level
    access, it will cause the docstring and :func:`repr` of the wrapped field
    to appear instead of the docstring and :func:`repr` of the wrapper.

    Wrappers of this type are suitable for computing :meth:`__hash__`, and for
    other scenarios in which a value must not change after construction.

    This wrapper does not inherit from AbstractField, because it behaves
    rather differently from real fields and would otherwise confuse some of
    the NBTObject machinery.  As a consequence, it will not be set to its
    default value by the standard NBTObject :meth:`__init__`.  If you want
    this functionality included, expose :attr:`wrapped` as an
    underscore-prefixed field.

    .. note::

        If the wrapped field is a :class:`MutableField`, the read-only
        restriction may not be observed if client code modifies the return
        value of :meth:`__get__` in-place.  Because this combination makes
        little sense anyway, a warning is raised when it occurs.

    """
    def __init__(self, wrapped: AbstractField):
        if isinstance(wrapped, MutableField):
            warnings.warn('A read-only MutableField is a contradiction in '
                          'terms.', category=exceptions.ClassWarning,
                          stacklevel=2)
        self._wrapped = wrapped

    def __get__(self, obj: NBT_OBJECT, owner: NBT_META=None) -> object:
        return self.wrapped.__get__(obj, owner)

    def __set__(self, obj: NBT_OBJECT, value: object):
        raise AttributeError('Immutable field')

    def __delete__(self, obj: NBT_OBJECT):
        raise AttributeError('Immutable field')

    @property
    def wrapped(self):
        """The wrapped field, which may be modified directly.

        It is recommended to expose this as an underscore-prefixed field on
        the class, as an escape-hatch for :meth:`__init__` and the like.  Such
        an underscore-prefixed field will also receive a :meth:`set_default`
        if :meth:`__init__` has not been overridden, and will appear in
        field-by-field introspection (while the immutable wrapper will not).

        """
        return self._wrapped


class MultiField(AbstractField):
    """Field combining multiple top-level tags into one object.

    Controls a series of one or more top-level tags which should be combined
    into a single Pythonic object.  If the tags are enclosed in a
    ``TAG_Compound``, consider using an :class:`NBTObjectField` instead.

    This is an abstract class.  :meth:`to_python` will be called with the same
    number of arguments as :obj:`nbt_names` has elements, in the same order
    specified, and should return a value acceptable to :meth:`from_python`,
    which should produce a sequence of the same values passed as arguments to
    :meth:`to_python`.

    If a tag does not exist, :meth:`to_python` will be passed :obj:`None`
    instead of the corresponding tag.  If :meth:`from_python` produces a
    :obj:`None` value, the corresponding tag will be skipped.

    :obj:`default` should be a value acceptable to :meth:`from_python`, which
    will be called when setting the field to its default value.

    """
    def __init__(self, nbt_names: (str, ...), *, default: object=None):
        self.nbt_names = nbt_names
        self.__doc__ = str(self)
        super().__init__(default=default)

    def __get__(self, obj: NBT_OBJECT, owner: NBT_META=None) -> object:
        if obj is None:
            return self
        raws = []
        for nbt_name in self.nbt_names:
            logger.debug('Retrieving value %s from %s object', nbt_name,
                         type(obj).__name__)
            raw_value = obj.data.get(nbt_name)
            raws.append(raw_value)
        args = tuple(raws)
        logger.debug('All values retrieved, converting to Pythonic')
        result = self.to_python(*args)
        return result

    def __set__(self, obj: NBT_OBJECT, value: object):
        if obj is None:
            raise AttributeError("Field is not settable at the class level.")
        if value is None:
            self.__delete__(obj)
            return
        logger.debug('Converting %r to NBT', value)
        raws = self.from_python(value)
        for nbt_name, raw_value in zip(self.nbt_names, raws):
            if raw_value is None:
                logger.debug('Skipping value %s (for %s object)', nbt_name,
                             type(obj).__name__)
                continue
            logger.debug('Storing value %s in %s object', nbt_name,
                         type(obj).__name__)
            obj.data[nbt_name] = raw_value

    def __delete__(self, obj: NBT_OBJECT):
        for name in self.nbt_names:
            with contextlib.suppress(KeyError):
                del obj.data[name]

    def __repr__(self) -> str:
        return ('<MultiField: nbt_names={!r}, default={!r}>'
                .format(self.nbt_names, self.default))

    def __str__(self) -> str:
        return "Multi-field combining {}".format(self.nbt_names)

    @abc.abstractmethod
    def to_python(self, *tags: (tags.TagMixin, ...)) -> object:
        """Transform several tags into a single Pythonic object."""
        raise NotImplementedError('MultiField does not implement to_python')

    @abc.abstractmethod
    def from_python(self, value: object) -> (tags.TagMixin, ...):
        """Transform a single Pythonic object into several tags."""
        raise NotImplementedError('MultiField does not implement from_python')


class SingleField(AbstractField):
    """Field for a single top-level tag.

    This is an abstract class.  :meth:`to_python` is passed an NBT tag (see
    :mod:`nbtparse.syntax.tags`) and should return some object.  That object
    should be acceptable to :meth:`from_python`, which should return the
    equivalent NBT tag.

    """
    def __init__(self, nbt_name: str, *, typename: str=None,
                 default: object=None):
        self.typename = typename
        self.nbt_name = nbt_name
        self.__doc__ = str(self)
        super().__init__(default=default)

    def __get__(self, obj: NBT_OBJECT, owner: NBT_META=None) -> object:
        if obj is None:
            return self
        try:
            raw_value = obj.data[self.nbt_name]
        except KeyError:
            return None
        return self.to_python(raw_value)

    def __set__(self, obj: NBT_OBJECT, value: object):
        if obj is None:
            raise AttributeError('Field not settable at the class level.')
        if value is None:
            try:
                self.__delete__(obj)
            except KeyError:
                pass
        else:
            raw_value = self.from_python(value)
            obj.data[self.nbt_name] = raw_value

    def __delete__(self, obj: NBT_OBJECT):
        del obj.data[self.nbt_name]

    def __repr__(self) -> str:
        return ('<SingleField: nbt_name={!r}, default={!r}>'
                .format(self.nbt_name, self.default))

    def __str__(self) -> str:
        if self.typename is not None:
            return "{} field called {}".format(self.typename, self.nbt_name)
        else:
            return "Field called {}".format(self.nbt_name)

    @abc.abstractmethod
    def to_python(self, tag: tags.TagMixin) -> object:
        """Transform this tag into a Pythonic object."""
        raise NotImplementedError('SingleField does not implement to_python')

    @abc.abstractmethod
    def from_python(self, value: object) -> tags.TagMixin:
        """Transform a Pythonic object into this tag."""
        raise NotImplementedError('SingleField does not implement '
                                  'from_python')


class TupleMultiField(MutableField, MultiField):
    """Field which combines several tags into a tuple.

    :obj:`to_pythons` and :obj:`from_pythons` should be sequences of functions
    which translate each item listed in :obj:`nbt_names` into its
    corresponding Python value.

    """
    def __init__(self, nbt_names: (str, ...),
                 to_pythons: (types.FunctionType, ...),
                 from_pythons: (types.FunctionType, ...), *,
                 default: (object, ...)=None):
        if default is None:
            default = (None,) * len(nbt_names)

        self.to_pythons = to_pythons
        self.from_pythons = from_pythons

        super().__init__(nbt_names, cache_key=nbt_names, default=default)

    def __repr__(self):
        return ('<TupleMultiField: nbt_names={!r}, default={!r}>'
                .format(self.nbt_names, self.default))

    def to_python(self, *raws: (tags.TagMixin, ...)) -> (object, ...):
        to_pythons = self.to_pythons
        return tuple(None if raw_value is None else func(raw_value)
                     for func, raw_value in zip(to_pythons, raws))

    def from_python(self, values: (object, ...)) -> (tags.TagMixin, ...):
        from_pythons = self.from_pythons
        return tuple(func(cooked_value) for func, cooked_value in
                     zip(from_pythons, values))


UUID_STRUCT = struct.Struct('>qq')


class UUIDField(MultiField):
    """Field which combines two ``TAG_Long``'s into a `UUID`_.

    A :obj:`default` of :obj:`None` will generate a new UUID every time.
    Assigning :obj:`None` in the ordinary fashion is equivalent to deleting
    the field.

    .. _UUID: http://en.wikipedia.org/wiki/UUID

    """
    def __init__(self, high_name: str, low_name: str, *,
                 default: uuid.UUID=None):
        nbt_names = (high_name, low_name)

        super().__init__(nbt_names, default=default)

    def __str__(self) -> str:
        return ("Universally unique identifier field split between {} "
                "and {}".format(*self.nbt_names))

    def __repr__(self) -> str:
        high_name, low_name = self.nbt_names
        return ('UUIDField({!r}, {!r}, default={!r})'
                .format(high_name, low_name, self.default))

    def set_default(self, obj: object):
        """If this field's default is :obj:`None`, generate a UUID."""
        if self.default is None:
            self.__set__(obj, uuid.uuid4())
        else:
            super().set_default(obj)

    @staticmethod
    def to_python(high_tag: tags.LongTag, low_tag: tags.LongTag) -> uuid.UUID:
        raw_bytes = UUID_STRUCT.pack(high_tag, low_tag)
        return uuid.UUID(bytes=raw_bytes)

    @staticmethod
    def from_python(uuid_instance: uuid.UUID) -> (tags.LongTag, tags.LongTag):
        raw_bytes = uuid_instance.bytes
        int_high, int_low = UUID_STRUCT.unpack(raw_bytes)
        return (tags.LongTag(int_high), tags.LongTag(int_low))


class BooleanField(SingleField):
    """Field for a ``TAG_Byte`` acting as a boolean."""
    def __init__(self, nbt_name: str, *, default: bool=False):
        super().__init__(nbt_name, typename="boolean", default=default)

    def __repr__(self) -> str:
        return 'BooleanField({!r}, default={!r})'.format(self.nbt_name,
                                                         self.default)

    @staticmethod
    def to_python(tag: tags.ByteTag) -> bool:
        return bool(tag)

    @staticmethod
    def from_python(value: bool) -> tags.ByteTag:
        return tags.ByteTag(value)


class ByteField(SingleField):
    """Field for a ``TAG_Byte`` acting as an integer."""
    def __init__(self, nbt_name: str, *, default: int=0):
        super().__init__(nbt_name, typename="byte", default=default)

    def __repr__(self) -> str:
        return ('ByteField({!r}, default={!r})'
                .format(self.nbt_name, self.default))

    @staticmethod
    def to_python(tag: tags.ByteTag) -> int:
        return int(tag)

    @staticmethod
    def from_python(value: int) -> tags.ByteTag:
        return tags.ByteTag(value)


class ShortField(SingleField):
    """Field for a ``TAG_Short``."""
    def __init__(self, nbt_name: str, *, default: int=0):
        super().__init__(nbt_name, typename="short integer", default=default)

    def __repr__(self) -> str:
        return ('ShortField({!r}, default={!r})'
                .format(self.nbt_name, self.default))

    @staticmethod
    def to_python(tag: tags.ShortTag) -> int:
        return int(tag)

    @staticmethod
    def from_python(value: int) -> tags.ShortTag:
        return tags.ShortTag(value)


class IntField(SingleField):
    """Field for a ``TAG_Int``."""
    def __init__(self, nbt_name: str, *, default: int=0):
        super().__init__(nbt_name, typename="integer", default=default)

    def __repr__(self) -> str:
        return 'IntField({!r}, default={!r})'.format(self.nbt_name,
                                                     self.default)

    @staticmethod
    def to_python(tag: tags.IntTag) -> int:
        return int(tag)

    @staticmethod
    def from_python(value: int) -> tags.IntTag:
        return tags.IntTag(value)


class LongField(SingleField):
    """Field for a ``TAG_Long``."""
    def __init__(self, nbt_name: str, *, default: int=0):
        super().__init__(nbt_name, typename="long integer", default=default)

    def __repr__(self) -> str:
        return 'LongField({!r}, default={!r})'.format(self.nbt_name,
                                                      self.default)

    @staticmethod
    def to_python(tag: tags.LongTag) -> int:
        return int(tag)

    @staticmethod
    def from_python(value: int) -> tags.LongTag:
        return tags.LongTag(value)


class FloatField(SingleField):
    """Field for a ``TAG_Float``."""
    def __init__(self, nbt_name: str, *, default: float=0.0):
        super().__init__(nbt_name, typename="floating point",
                         default=default)

    def __repr__(self):
        return 'FloatField({!r}, default={!r})'.format(self.nbt_name,
                                                       self.default)

    @staticmethod
    def to_python(tag: tags.FloatTag) -> int:
        return float(tag)

    @staticmethod
    def from_python(value: int) -> tags.FloatTag:
        return tags.FloatTag(value)


class DoubleField(SingleField):
    """Field for a ``TAG_Double``."""
    def __init__(self, nbt_name: str, *, default: float=0.0):
        super().__init__(nbt_name, typename="floating point (high "
                         "precision)", default=default)

    def __repr__(self) -> str:
        return ('DoubleField({!r}, default={!r})'
                .format(self.nbt_name, self.default))

    @staticmethod
    def to_python(tag: tags.DoubleTag) -> int:
        return float(tag)

    @staticmethod
    def from_python(value: int) -> tags.DoubleTag:
        return tags.DoubleTag(value)


class ByteArrayField(MutableField, SingleField):
    """Field for a ``TAG_Byte_Array``."""
    def __init__(self, nbt_name: str, *, default: bytearray=None):
        if default is None:
            default = bytearray()
        super().__init__(nbt_name, typename="string (8-bit)",
                         cache_key=nbt_name, default=default)

    def __repr__(self) -> str:
        return ('ByteArrayField({!r}, default={!r})'
                .format(self.nbt_name, self.default))

    @staticmethod
    def to_python(tag: tags.ByteArrayTag) -> bytearray:
        return bytearray(tag)

    @staticmethod
    def from_python(value: bytearray) -> tags.ByteArrayTag:
        return tags.ByteArrayTag(value)


class UnicodeField(SingleField):
    """Field for a ``TAG_String``."""
    def __init__(self, nbt_name: str, *, default: str=''):
        super().__init__(nbt_name, typename="string (unicode)",
                         default=default)

    def __repr__(self) -> str:
        return 'UnicodeField({!r}, default={!r})'.format(self.nbt_name,
                                                         self.default)

    @staticmethod
    def to_python(tag: tags.StringTag) -> str:
        return str(tag)

    @staticmethod
    def from_python(value: str) -> tags.StringTag:
        return tags.StringTag(value)


class IntArrayField(MutableField, SingleField):
    """Field for a ``TAG_Int_Array``."""
    def __init__(self, nbt_name: str, *, default: list=()):
        super().__init__(nbt_name, default=default, cache_key=nbt_name)

    def __repr__(self) -> str:
        return 'IntArrayField({!r}, default={!r}'.format(self.nbt_name,
                                                         self.default)

    @staticmethod
    def to_python(tag: tags.IntArrayTag) -> list:
        return list(tag)

    @staticmethod
    def from_python(value: list) -> tags.IntArrayTag:
        return tags.IntArrayTag(value)


EPOCH = datetime.datetime.utcfromtimestamp(0)
EPOCH = EPOCH.replace(tzinfo=datetime.timezone.utc)


class UTCField(SingleField):
    """Field for a ``TAG_Long`` holding a `Unix timestamp`_.

    Note that this is always in UTC.  See :mod:`datetime` for documentation.

    .. _Unix timestamp: http://en.wikipedia.org/wiki/Unix_time

    """
    def __init__(self, nbt_name: str, *, default: datetime.datetime=EPOCH):
        super().__init__(nbt_name, typename="UTC timestamp", default=default)

    def __repr__(self) -> str:
        return ('UTCField({!r}, default={!r})'.format(self.nbt_name,
                                                      self.default))

    @staticmethod
    def to_python(nbt: tags.LongTag) -> datetime.datetime:
        try:
            result = datetime.datetime.utcfromtimestamp(nbt)
        except ValueError:
            return None
        else:
            return result.replace(tzinfo=datetime.timezone.utc)

    @staticmethod
    def from_python(dt: datetime.datetime) -> tags.LongTag:
        posix_time = dt.timestamp()
        return tags.LongTag(posix_time)


class NBTObjectField(MutableField, SingleField):
    """Field for an :class:`~nbtparse.semantics.nbtobject.NBTObject`.

    Usually a ``TAG_Compound`` but exact contents will vary.

    In other words, a brand-new instance of the object will be created, with
    all its fields set to their default values.

    """
    def __init__(self, nbt_name: str, obj_class: NBT_META, *,
                 default: NBT_OBJECT=None):
        self.obj_class = obj_class
        super().__init__(nbt_name, typename="NBTObject", cache_key=nbt_name,
                         default=default)

    def __repr__(self) -> str:
        return ('NBTObjectField({!r}, {}, default={!r})'
                .format(self.nbt_name, self.obj_class.__name__, self.default))

    @staticmethod
    def to_python(nbt: tags.TagMixin) -> NBT_OBJECT:
        return self.obj_class.from_nbt(nbt)

    @staticmethod
    def from_python(obj: NBT_OBJECT) -> tags.TagMixin:
        return obj.to_nbt()


class ListField(MutableField, SingleField):
    """Field for a ``TAG_List``.

    The ListTag will be given an id of :obj:`content_id` for the elements.

    """
    def __init__(self, nbt_name: str, item_to_python: types.FunctionType,
                 item_from_python: types.FunctionType, content_id: int,
                 *, default: list=()):
        self.item_to_python = item_to_python
        self.item_from_python = item_from_python
        self.content_id = content_id
        super().__init__(nbt_name, typename="list", cache_key=nbt_name,
                         default=default)

    def __repr__(self) -> str:
        return ('<ListField: nbt_name={!r}, contend_id={!r}, default={!r}>'
                .format(self.nbt_name, self.content_id, self.default))

    def to_python(self, l: tags.ListTag) -> list:
        if l is None:
            return None
        return list(map(self.item_to_python, l))

    def from_python(self, l: list) -> tags.ListTag:
        if l is None:
            return None
        return tags.ListTag(list(map(self.item_from_python, l)),
                            self.content_id)


class ObjectListField(ListField):
    """Field for a ``TAG_List`` of :class:`~.nbtobject.NBTObject`\ s."""
    def __init__(self, nbt_name: str, obj_class: NBT_META, *,
                 default: list=()):
        item_to_python = obj_class.from_nbt
        item_from_python = lambda item: item.to_nbt()
        self.obj_class_name = obj_class.__name__
        super().__init__(nbt_name, item_to_python, item_from_python,
                         ids.TAG_Compound, default=default)

    def __repr__(self) -> str:
        return ('ObjectListField({!r}, {}, default={!r})'
                .format(self.nbt_name, self.obj_class_name, self.default))


class TupleListField(MutableField, SingleField):
    """Field for a ``TAG_List``; converts to a tuple.

    This should not be confused with :class:`TupleMultiField`, which takes
    several top-level tags and wraps them together into a single field.  This
    takes a single ``TAG_List`` and converts it into a tuple.
    :class:`ListField` takes a single TAG_List and converts it into a list.

    """
    def __init__(self, nbt_name: str, item_to_python: types.FunctionType,
                 item_from_python: types.FunctionType, content_id: int,
                 *, default: (object, ...)=()):
        self.item_to_python = item_to_python
        self.item_from_python = item_from_python
        self.content_id = content_id
        super().__init__(nbt_name, typename="tuple", cache_key=nbt_name,
                         default=default)

    def to_python(self, l: tags.ListTag) -> tuple:
        if l is None:
            return None
        return tuple(map(self.item_to_python, l))

    def from_python(self, l: tuple) -> tags.ListTag:
        if l is None:
            return None
        return tags.ListTag(list(map(self.item_from_python, l)),
                            self.content_id)


class ObjectTupleField(TupleListField):
    """Field for a ``TAG_List`` of :class:`.NBTObject`\ s, as a tuple."""
    def __init__(self, nbt_name: str, obj_class: NBT_META, *,
                 default: (NBT_OBJECT, ...)=()):
        item_to_python = obj_class.from_nbt
        item_from_python = lambda item: item.to_nbt()
        super().__init__(nbt_name, item_to_python, item_from_python,
                         ids.TAG_Compound, default=default)


class EnumField(SingleField):
    """Field for an enumerated type.

    See :mod:`enum`.

    """
    def __init__(self, nbt_name: str, enum_class: type(enum.Enum), *,
                 tag_type: type=tags.IntTag, default: enum.Enum=None):
        self.enum_class = enum_class
        self.tag_type = tag_type
        super().__init__(nbt_name, default=default)

    def to_python(self, number: tags.TagMixin) -> enum.Enum:
        return self.enum_class(number)

    def from_python(self, enum_value: enum.Enum) -> tags.TagMixin:
        return self.tag_type(enum_value.value)


def self_reference(field_name: str, nbt_name: str) -> types.FunctionType:
    """Class decorator to allow a class's fields to refer to the class itself.

    Typical usage::

        @self_reference('parent', u'ParentFoo')
        class Foo(NBTObject):
            pass

    Now :obj:`Foo.parent` is an :class:`NBTObjectField` for a :class:`Foo`.

    """
    def decorator(cls: NBT_META) -> NBT_META:
        field = NBTObjectField(nbt_name, cls)
        type(cls).attach_field(cls, field, field_name)
        return cls
    return decorator
