"""Classes for projectiles, such as snowballs and arrows."""

from ..syntax import tags, ids
from ..semantics import fields
from . import entity, item


PICKUP_NOBODY = 0
PICKUP_ANYBODY = 1
PICKUP_CREATIVE = 2


class Projectile(entity.Entity):
    """A projectile.

    A fast-moving entity like an arrow or snowball.

    """
    coords = fields.TupleMultiField(('xTile', 'yTile', 'zTile'),
                                    (int,) * 3, (tags.ShortTag,) * 3,
                                    default=(0,) * 3)
    in_tile = fields.ByteField('inTile')
    shake = fields.ByteField('shake')
    in_ground = fields.BooleanField('inGround')


class Egg(Projectile, id='Egg'):
    """A thrown egg."""
    pass


class Arrow(Projectile, id='Arrow'):
    """An arrow.

    Fired by a player or a skeleton.
    """
    in_data = fields.ByteField('inData')
    pickup = fields.IntField('pickup')
    player = fields.BooleanField('player')
    damage = fields.DoubleField('damage')


class AbstractFireball(Projectile):
    """Any fireball-like thing."""
    direction = fields.TupleListField('direction', float, tags.DoubleTag,
                                      ids.TAG_Double, default=(0.0,)*3)


class Fireball(AbstractFireball, id='Fireball'):
    """A regular fireball."""
    pass


class SmallFireball(AbstractFireball, id='SmallFireball'):
    """A small fireball."""
    pass


class WitherSkull(AbstractFireball, id='WitherSkull'):
    """A wither skull."""
    pass


class Thrown(Projectile):
    """Anything thrown by players (and only players)."""
    owner_name = fields.UnicodeField('ownerName')


class ThrownEnderpearl(Thrown, id='ThrownEnderpearl'):
    """A thrown enderpearl.

    Teleports the player on landing.

    """
    pass


class ThrownExpBottle(Thrown, id='ThrownExpBottle'):
    """A thrown Bottle o' Enchanting."""
    pass


class ThrownPotion(Thrown, id='ThrownPotion'):
    """A thrown splash potion."""
    potion = fields.NBTObjectField('Potion', item.Item)
    potion_value = fields.IntField('potionValue')


class ThrownSnowball(Thrown, id='Snowball'):
    """A thrown snowball."""
    pass
