"""Classes for Minecraft entities."""

import logging
import warnings

from ..syntax import tags
from ..syntax import ids as tag_ids
from ..semantics import fields, nbtobject
from .. import exceptions
from . import ids, entity_ids


logger = logging.getLogger(__name__)


class EntityMeta(nbtobject.NBTMeta):
    """Metaclass for entities.

    The ID of the entity should be passed as a class keyword argument called
    id, as follows::

        class FooEntity(Entity, id='namespace:foo'):
            pass

    This will create a top-level field with the given string as its default
    value, for the entity's ID.  If the class is declared at the top level of
    its module, this will also register it via
    :mod:`entity_ids`, in the :class:`~entity_ids.EntityNamespace`
    called ``'namespace'``.  If no namespace is specified, the empty string is
    assumed.

    .. note::

        The empty string namespace is reserved for use by application code.
        Third-party libraries should always specify a namespace.  The
        namespace ``'minecraft'`` is reserved for entities which exist in
        vanilla Minecraft.

    """
    def __new__(mcs, names, bases, dct, *args, id=None, **kwargs):
        cls = super().__new__(mcs, names, bases, dct, *args, **kwargs)
        if id is not None:
            *namespace, identifier = str(id).split(':')
            namespace, = namespace if namespace else ('',)
            del id  # Don't shadow a builtin longer than absolutely necessary
            if '.' in cls.__qualname__:
                logger.debug('Not registering %r: dot in qualname', cls)
            else:
                cls = entity_ids.register_class(identifier, namespace)(cls)
            field = fields.UnicodeField('id', default=identifier)
            field.__doc__ = """Usually equal to {!r}""".format(identifier)
            cls.id = field
        return cls

    def __init__(cls, name, bases, dct, *args, id=None, namespace='',
                 **kwargs):
        super().__init__(name, bases, dct, *args, **kwargs)


class CoordinateField(fields.TupleListField):
    """Field for a ``TAG_List`` of coordinates.

    Pythonic equivalent is a tuple with two or three elements depending on
    whether or not Y is included.  Elements may be ints or floats depending on
    the underlying datatype.

    """
    def __init__(self, nbt_name: str, has_y: bool, fractional: bool):
        if fractional:
            item_to_python = float
            item_from_python = tags.DoubleTag
            content_id = tag_ids.TAG_Double
            if has_y:
                default = (0.0,) * 3
            else:
                default = (0.0,) * 2
        else:
            item_to_python = int
            item_from_python = tags.IntTag
            content_id = tag_ids.TAG_Int
            if has_y:
                default = (0,) * 3
            else:
                default = (0,) * 2
        self.has_y = has_y
        self.fractional = fractional
        super(CoordinateField, self).__init__(nbt_name, item_to_python,
                                              item_from_python, content_id,
                                              default=default)

    def __set__(self, obj: object, value: (int, int, ...)):
        if obj is None:
            super(CoordinateField, self).__set__(obj, value)
            return
        if self.has_y and len(value) != 3:
            raise ValueError("Wrong number of coordinates: expected 3.")
        elif not self.has_y and len(value) != 2:
            raise ValueError("Wrong number of coordinates: expected 2.")
        super(CoordinateField, self).__set__(obj, value)

    def __repr__(self):
        return 'CoordinateField({!r}, {!r}, {!r})'.format(self.nbt_name,
                                                          self.has_y,
                                                          self.fractional)


@fields.self_reference('mount', 'Riding')
class Entity(nbtobject.NBTObject, metaclass=EntityMeta):
    """A Minecraft entity.

    Subclasses of :class:`Entity` may be declared with an extra parameter like
    this::

        class Foo(Entity, id='Foo'):
            pass

    Such subclasses have an ID field attached to them automatically, with an
    appropriate default value.

    Entities are hashable and compare equal if they have the same UUID (and
    the same :func:`type`).

    """
    id = fields.UnicodeField('id')
    id.__doc__ = """What kind of entity this is.

    :mod:`.entityfactory` can use this to create subclasses of :class:`Entity`
    automatically.

    """
    pos = CoordinateField('Pos', has_y=True, fractional=True)
    pos.__doc__ = """Position of this entity, in (x, y, z) form.

    Values may be fractional.

    """
    motion = CoordinateField('Motion', has_y=True, fractional=True)
    motion.__doc__ = """Velocity at which this entity is moving.

    Stored as an (x, y, z) tuple.

    """
    rotation = CoordinateField('Rotation', has_y=False, fractional=True)
    rotation.__doc__ = """Rotation of this entity.

    Stored as (yaw, pitch).  Roll is not supported.

    """
    fall_distance = fields.FloatField('FallDistance')
    fall_distance.__doc__ = """Distance this entity has fallen.

    Farther distances will result in greater fall damage on landing.

    """
    fire_ticks = fields.ShortField('Fire')
    fire_ticks.__doc__ = """How much longer this entity will be aflame.

    Equal to -1 if not on fire.  Larger negative values make it temporarily
    fireproof.

    """
    air_ticks = fields.ShortField('Air')
    air_ticks.__doc__ = """How much longer until this entity begins to drown.

    Starts at 300 when above water and goes down when underwater.  At zero,
    lose 1 health per second.

    """
    on_ground = fields.BooleanField('OnGround')
    on_ground.__doc__ = """Whether this entity is touching the ground."""
    dimension = fields.IntField('Dimension')
    dimension.__doc__ = """Which dimension we're in.

    .. note::

        This information is stored elsewhere; it is not known why Minecraft
        stores it here as well.

    """
    invulnerable = fields.BooleanField('Invulnerable')
    invulnerable.__doc__ = """Whether entity is immune to all damage.

    Also applies to nonliving entities.

    """
    portal_cooldown = fields.IntField('PortalCooldown')
    portal_cooldown.__doc__ = (
        """Number of ticks until this entity passes through a portal.

        Starts at 900 and counts down when in a portal.  Switch dimensions at
        zero.

        """)
    uuid = fields.ReadOnly(fields.UUIDField('UUIDMost', 'UUIDLeast'))
    _uuid = uuid.wrapped
    _uuid.__doc__ = """`Universally unique identifier`_ for this entity.

    .. _Universally unique identifier: http://en.wikipedia.org/wiki/UUID

    Should be unique across *every* Minecraft world.  Cannot be changed once
    the entity is constructed.  Creating a new entity will set this to a new
    UUID.

    If it is necessary to initialize this field, you may modify :attr:`_uuid`
    instead.  This field is a wrapper for that value.  As the name suggests,
    it must not be modified outside :meth:`__init__`.  Since the UUID is used
    in calculating the :func:`hash`, violating this rule is a Bad Idea.

    """

    def __eq__(self, other):
        return type(self) is type(other) and self.uuid == other.uuid

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((type(self), self.uuid))

    def __repr__(self):
        name = type(self).__name__
        return '<{}: id={!r}, pos={!r}, uuid={!r}>'.format(name,
                                                           self.id,
                                                           self.pos,
                                                           self.uuid)
