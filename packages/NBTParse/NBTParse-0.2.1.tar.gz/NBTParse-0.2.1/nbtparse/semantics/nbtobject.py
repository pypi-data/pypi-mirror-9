"""NBT high-level object-oriented class

:class:`NBTObject` is an object-oriented wrapper for
:class:`~.tags.CompoundTag`, designed to expose its fields in a standard and
well-documented fashion.

"""
from collections import abc as cabc
import io
import logging
import reprlib
import warnings

from ..syntax import tags
from .. import exceptions
from . import fields


fields_mod = fields  # to avoid name collisions


logger = logging.getLogger(__name__)


class NBTMeta(type):
    """Metaclass for NBTObjects.

    Allows NBTObjects to track their fields upon creation.

    """
    def __init__(cls, name, bases, dct):
        if '_cached' in dct:
            warnings.warn('The name _cached is used internally by NBTObject.',
                          category=exceptions.ClassWarning, stacklevel=2)
        class_fields = {}
        for base in reversed(cls.__mro__):
            try:
                field_dict = base.__fields
            except AttributeError:
                continue
            else:
                class_fields.update(field_dict)
        for key, value in dct.items():
            if isinstance(value, fields.AbstractField):
                class_fields[key] = value
        cls.__fields = class_fields
        super().__init__(name, bases, dct)

    def fields(cls) -> cabc.Set:
        """Return a set of the public fields attached to this class.

        The elements of the set are strings whose names correspond to those of
        the fields.  They are suitable arguments for :func:`getattr` and
        :func:`setattr`.

        Does not include fields whose names begin with underscores.

        """
        return set(key for key in cls.__fields if not key.startswith('_'))

    def all_fields(cls) -> cabc.Set:
        """Return a set of all fields attached to this class.

        Includes fields whose names begin with underscores.

        """
        return set(cls.__fields)

    def attach_field(cls, field: fields_mod.AbstractField, field_name: str):
        """Attaches the given field with the given name to the class.

        Changing a class after it's created is usually a Bad Idea; this method
        is meant to be used in class decorators and other contexts where you
        can be reasonably sure the class has not yet been instantiated.

        """
        setattr(cls, field_name, field)
        cls.__fields[field_name] = field

    def detach_field(cls, field_name: str):
        """Detaches the field with the given name from the class.

        Changing a class after it's created is usually a Bad Idea; this method
        is meant to be used in class decorators and other contexts where you
        can be reasonably sure the class has not yet been instantiated.

        """
        delattr(cls, field_name)
        del cls.__fields[field_name]


class NBTObject(metaclass=NBTMeta):
    """Thin wrapper over a ``TAG_Compound``.

    Typically houses one or more :mod:`fields<nbtparse.semantics.fields>`.

    Calling the constructor directly will create an empty object with all
    fields set to their default values, except for any specifically
    initialized as keyword arguments.  Calling :meth:`from_nbt` will populate
    fields from the provided NBT.

    .. note:: If the default of a field is :obj:`None`, that field will be set
       to :obj:`None`, which is equivalent to leaving it empty.  Such fields
       will not be present in the generated NBT unless their values are
       changed by hand.  In some cases, this means newly created objects will
       require modification before they can be meaningfully saved.

       Some fields don't observe the above semantics and will do something
       different when the default is None.  This is noted in the
       :mod:`~.semantics.fields` documentation where applicable.  Such fields
       will still erase their contents if explicitly set to None.

    """
    def __init__(self, *args, **kwargs):
        logger.debug('Creating new empty %s instance', type(self))
        #: The underlying :class:`~.tags.CompoundTag` for this NBTObject.
        #:
        #: Fields store and retrieve instance data in this attribute.  It is
        #: largely used as-is when calling :meth:`to_nbt`, but some fields may
        #: customize this process in their :meth:`~.fields.AbstractField.save`
        #: methods.  Some NBTObjects will also alter the output by overriding
        #: :meth:`to_nbt`.  For these reasons, direct manipulation of this
        #: attribute is discouraged.  It may still prove useful for debugging
        #: or for cases where a key is not controlled by any field.
        self.data = tags.CompoundTag()
        self._cached = {}  # from NBT name to cached Python object
        all_fields = self.all_fields()
        public_fields = self.fields()
        for name in all_fields:
            field = getattr(type(self), name)
            if name in public_fields:
                try:
                    value = kwargs.pop(name)
                except KeyError:
                    pass  # see below
                else:
                    logger.debug('Setting %r to %r', field, value)
                    field.__set__(self, value)
                    continue
            logger.debug('Setting default value for %r', field)
            field.set_default(self)
        super().__init__(*args, **kwargs)

    def to_nbt(self) -> tags.CompoundTag:
        """Returns an NBT representation of this object.

        By default, return self.data, which is sufficient if all data is
        kept in fields.

        Also calls the :meth:`~.fields.AbstractField.save` methods of all the
        fields.

        """
        logger.debug('Converting %r to NBT', self)
        for name in self.all_fields():
            field = getattr(type(self), name)
            logger.debug('Saving %r', field)
            field.save(self)
        result = tags.CompoundTag(self.data)
        return self.prepare_save(result)

    def prepare_save(self, nbt: tags.CompoundTag) -> tags.CompoundTag:
        """Hook called during :meth:`to_nbt` with the to-be-saved NBT.

        Should return a :class:`~.tags.CompoundTag` after (for instance)
        wrapping data inside a singleton CompoundTag or performing other
        transformations.

        Unless overridden, return argument unchanged.

        This hook runs after all fields'
        :meth:`~.fields.AbstractField.save` methods are called.  It is the
        last hook before the NBT is saved.

        """
        return nbt

    @classmethod
    def from_nbt(cls, nbt: tags.CompoundTag):
        """Creates a new NBTObject from the given NBT representation.

        Stores the given NBT in the data attribute of the newly-created
        object.

        Also calls the :meth:`~.fields.AbstractField.load` methods of all the
        fields.

        """
        if nbt is None:
            raise TypeError('Cannot create empty NBTObject via from_nbt')
        logger.debug('Creating %s from NBT', cls)
        nbt = tags.CompoundTag(nbt)
        nbt = cls.prepare_load(nbt)
        result = super().__new__(cls)
        result.data = nbt
        result._cached = {}
        for name in cls.all_fields():
            field = getattr(cls, name)
            logger.debug('Loading %r', field)
            field.load(result)
        return result

    @classmethod
    def prepare_load(cls, nbt: tags.CompoundTag) -> tags.CompoundTag:
        """Hook called during :meth:`from_nbt` with the loaded NBT.

        Should return a :class:`~.tags.CompoundTag` after (for instance)
        unwrapping data inside a singleton CompoundTag or performing other
        transformations.

        Unless overridden, return argument unchanged.

        This hook runs before any fields'
        :meth:`~.fields.AbstractField.load` methods are called.  It is the
        first hook after the NBT has been loaded.

        .. note::

            Unlike :meth:`prepare_save`, this method must be callable as a
            class method.  In practice, both methods can often be implemented
            as static methods anyway.

        """
        return nbt

    def to_bytes(self) -> bytes:
        """Serialize this NBTObject directly to a :class:`bytes` object.

        The root tag will have no name.

        """
        result = io.BytesIO()
        nbt = self.to_nbt()
        nbt.encode_named('', result)
        return result.getvalue()

    @classmethod
    def from_bytes(cls, raw: bytes):
        """Deserialize a new NBTObject from a :class:`bytes` object.

        The name of the root tag is discarded.

        """
        buf = io.BytesIO(raw)
        _, nbt = tags.CompoundTag.decode_named(buf)
        return cls.from_nbt(nbt)

    @classmethod
    def fields(cls) -> cabc.Set:
        """Forwards to :meth:`NBTMeta.fields`, which see."""
        return type(cls).fields(cls)

    @classmethod
    def all_fields(cls) -> cabc.Set:
        """Forwards to :meth:`NBTMeta.all_fields`, which see."""
        return type(cls).all_fields(cls)

    def __reduce__(self):
        return (_from_nbt, (type(self), self.to_nbt(),))

    def __repr__(self):
        return '<NBTObject: {}>'.format(reprlib.repr(self.data))


def _from_nbt(klass, nbt):
    """Helper function for unpickling.

    Don't use.

    """
    return klass.from_nbt(nbt)
