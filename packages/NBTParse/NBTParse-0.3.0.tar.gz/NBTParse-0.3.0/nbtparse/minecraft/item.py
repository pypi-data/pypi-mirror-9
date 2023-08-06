"""Classes for items and XP orbs."""

from ..semantics import nbtobject, fields
from . import entity


class Item(nbtobject.NBTObject):
    """An inventory item.

    Not an entity; only stores item-related information.

    """
    slot = fields.ByteField('Slot')
    id = fields.UnicodeField('id')
    damage = fields.ShortField('Damage')
    count = fields.ByteField('Count')
    # TODO: Implement tags

    def __repr__(self):
        return '<Item: id={!r}, damage={!r}, count={!r}>'.format(self.id,
                                                                 self.damage,
                                                                 self.count)


class ItemEntity(entity.Entity):
    """Superclass of dropped item and XP orbs."""
    health = fields.ShortField('Health')
    age = fields.ShortField('Age')

    def __repr__(self):
        return ('<ItemEntity: id={!r}, pos={!r}, uuid={!r}, age={!r}, '
                'health={!r}>'.format(self.id, self.pos, self.uuid, self.age,
                                      self.health))


class DroppedItem(ItemEntity, id='Item'):
    """An item dropped on the ground."""
    item = fields.NBTObjectField('Item', Item)

    def __repr__(self):
        return ('<DroppedItem: pos={!r}, uuid={!r}, age={!r}, health={!r}, '
                'item: {!r}>'.format(self.pos, self.uuid, self.age,
                                     self.health, self.item))


class XPOrb(ItemEntity, id='XPOrb'):
    """An experience orb."""
    value = fields.ShortField('Value')

    def __repr__(self):
        return ('<XPOrb: value={!r}, age={!r}, health={!r}>'
                .format(self.value, self.age, self.health))
