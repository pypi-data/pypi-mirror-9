from ...syntax import tags
from ...semantics import nbtobject, fields
from .. import item, entity


class TileEntity(nbtobject.NBTObject, metaclass=entity.EntityMeta):
    """A tile entity.  Stores additional data about a block."""
    id = fields.UnicodeField('id')
    id.__doc__ = """A string identifying the type of tile entity."""
    coords = fields.TupleMultiField(('x', 'y', 'z'), (int,)*3,
                                    (tags.IntTag,)*3)
    coords.__doc__ = """The coordinates of this tile entity.

    .. note ::

        :class:`.region.Region` will usually overwrite this attribute with the
        appropriate value; you do not need to work with it directly.

    """


class Container(TileEntity):
    """One of several different kinds of containers.

    Consult the id to determine which kind.

    """
    custom_name = fields.UnicodeField('CustomName')
    custom_name.__doc__ = """The custom name of this container.

    Rename using an anvil.

    """
    lock = fields.UnicodeField('Lock')
    lock.__doc__ = """Optional string specifying a "lock item."

    Players not carrying the lock item will be unable to open the container.

    """


class Beacon(TileEntity, id='Beacon'):
    """A beacon."""
    levels = fields.IntField('Levels')
    levels.__doc__ = """How tall the pyramid is"""
    primary = fields.IntField('Primary')
    primary.__doc__ = """The primary power selected (as a potion ID)"""
    secondary = fields.IntField('Secondary')
    secondary.__doc__ = """The secondary power selected (as a potion ID)"""


class Cauldron(Container, id='Cauldron'):
    """A brewing stand (not actually a cauldron)."""
    items = fields.ObjectListField('Items', item.Item)
    items.__doc__ = """The items in the brewing stand.

    Slots numbered from 0 to 3 inclusive.

    """
    brew_time = fields.IntField('BrewTime')
    brew_time.__doc__ = """How long the brewing stand has been brewing.

    Measured in ticks.

    """


class Chest(Container, id='Chest'):
    """A single chest.  Double chests are two of these next to each other."""
    items = fields.ObjectListField('Items', item.Item)
    items.__doc__ = """List of items in the chest.

    Slots go from 0 to 26.  0 is the top left corner.

    """


class Comparator(TileEntity, id='Comparator'):
    """A comparator."""
    output = fields.IntField('OutputSignal')
    output.__doc__ = """Strength of the output signal.

    Will very likely be overwritten on the next block update.

    """


class Control(Container, id='Control'):
    """A control block."""
    command = fields.UnicodeField('Command')
    command.__doc__ = """The command to send on activation."""
    success_count = fields.IntField('SuccessCount')
    success_count.__doc__ = """Strength of the redstone output.

    Used for commands like ``/testfor``.  Only updates on activation.

    """
    last_output = fields.UnicodeField('LastOutput')
    last_output.__doc__ = """Output from most-recently executed command."""
    track_output = fields.BooleanField('TrackOutput')
    track_output.__doc__ = """Unknown."""


class DaylightSensor(TileEntity, id='DLDetector'):
    """A daylight sensor."""
    pass


class EndPortal(TileEntity, id='Airportal'):
    """An end portal."""
    pass


class FlowerPot(TileEntity, id='FlowerPot'):
    """A flower pot."""
    item = fields.IntField('Item')
    item.__doc__ = """Block ID of the contents of the pot.

    Most block ID's will not work; generally only plants are allowed.

    """
    flower_type = fields.IntField('Data')
    flower_type.__doc__ = """Data value of the contents of the pot."""


class Furnace(Container, id='Furnace'):
    """A furnace."""
    burn_time = fields.ShortField('BurnTime')
    burn_time.__doc__ = """Number of ticks of fuel remaining."""
    cook_time = fields.ShortField('CookTime')
    cook_time.__doc__ = """Number of ticks current item has been cooking for

    When this reaches 300, item is done.

    """
    items = fields.ObjectListField('Items', item.Item)
    items.__doc__ = """List of items, with slot field.

    Slot 0 is the cooking item, slot 1 is the fuel, and slot 2 is the output.

    """


class Hopper(Container, id='Hopper'):
    """A hopper."""
    items = fields.ObjectListField('Items', item.Item)
    items.__doc__ = """Items in the hopper"""
    cooldown = fields.IntField('TransferCooldown')
    cooldown.__doc__ = """Time until the next transfer.

    Zero if no transfer is imminent.

    """


class SpawnPotential(nbtobject.NBTObject):
    """One possible spawn from a spawner."""
    type = fields.UnicodeField('Type')
    type.__doc__ = """ID of the entity to spawn"""
    weight = fields.IntField('Weight')
    weight.__doc__ = """Relative likelihood that this spawn will be used.

    Must be positive.

    """
    properties = fields.NBTObjectField('Properties', nbtobject.NBTObject)
    properties.__doc__ = """Tags to copy to the entity to spawn."""


class Spawner(TileEntity, id='MobSpawner'):
    """A mob spawner."""
    spawn_potentials = fields.ObjectListField('SpawnPotentials',
                                              SpawnPotential)
    spawn_potentials.__doc__ = """List of :class:`SpawnPotential`\ s.

    Used to fill in some of the fields of this object after each spawn.

    """
    entity_id = fields.UnicodeField('EntityId')
    entity_id.__doc__ = """The ID of the next entity spawned."""
    spawn_data = fields.NBTObjectField('SpawnData', nbtobject.NBTObject)
    spawn_data.__doc__ = """Tags to copy to the next entity spawned."""
    spawn_count = fields.ShortField('SpawnCount')
    spawn_count.__doc__ = """Number of mobs to spawn at once."""
    spawn_range = fields.ShortField('SpawnRange')
    spawn_range.__doc__ = """How far away from the spawner to spawn.

    X and Y are both indepently constrained by this radius, so the target area
    is square rather than circular.

    """
    delay = fields.ShortField('Delay', default=-1)
    delay.__doc__ = """Time until next spawn in ticks.

    If set to -1 (the default for newly-created Spawners), randomize this
    value, :obj:`entity_id`, and :obj:`spawn_data` when a player comes in
    range.

    """
    min_delay = fields.ShortField('MinSpawnDelay')
    min_delay.__doc__ = """
    Minimum allowed delay, when Minecraft generates it."""
    max_delay = fields.ShortField('MaxSpawnDelay', default=1)
    max_delay.__doc__ = """
    Maximum allowed delay, when Minecraft generates it."""
    max_entities = fields.ShortField('MaxNearbyEntities')
    max_entities.__doc__ = """Maximum entities to spawn.

    If this is exceeded, stop spawning until some of the entities go out of
    range.

    """
    player_range = fields.ShortField('RequiredPlayerRange')
    player_range.__doc__ = """Maximum distance from a player.

    If no player is within this range, the spawner will shut down.

    """


class Music(TileEntity, id='Music'):
    """A music block."""
    note = fields.ByteField('note')
    note.__doc__ = """Pitch of the block.

    Every right click increases this by 1.  In music theory terms, this
    measures the number of semitones above F# (octave 3).  Values may range
    from 0 to 24 inclusive, or two full octaves.

    """


class Piston(TileEntity, id='Piston'):
    """A piston."""
    block_id = fields.IntField('blockId')
    block_id.__doc__ = """Block ID of the moving block."""
    block_data = fields.IntField('blockData')
    block_data.__doc__ = """Data (damage) value of the moving block."""
    facing = fields.IntField('facing')
    facing.__doc__ = """Direction the piston is facing."""
    progress = fields.FloatField('progress')
    progress.__doc__ = """How far the block has moved."""
    extending = fields.BooleanField('extending')
    extending.__doc__ = """Whether we are extending."""


class RecordPlayer(TileEntity, id='RecordPlayer'):
    """A jukebox."""
    record_id = fields.IntField('Record')
    record_id.__doc__ = """Item ID of the record being played.

    Zero if the jukebox is empty.

    """
    record_item = fields.NBTObjectField('RecordItem', item.Item)
    record_item.__doc__ = """The record in the jukebox.

    Can place other items here as well.

    """


class Sign(TileEntity, id='Sign'):
    """A sign."""
    line1 = fields.UnicodeField('Text1')
    line1.__doc__ = """First line of text.

    If longer than 16 characters, excess is discarded.

    """
    line2 = fields.UnicodeField('Text2')
    line2.__doc__ = """Second line of text."""
    line3 = fields.UnicodeField('Text3')
    line3.__doc__ = """Third line of text."""
    line4 = fields.UnicodeField('Text4')
    line4.__doc__ = """Fourth (last) line of text."""


class Skull(TileEntity, id='Skull'):
    """A skull on the ground."""
    skull_id = fields.ByteField('SkullType')
    skull_id.__doc__ = """Data value of the skull."""
    skull_name = fields.UnicodeField('ExtraType')
    skull_name.__doc__ = """Name of player whose skull it is."""
    rotation = fields.ByteField('Rot')
    rotation.__doc__ = """Rotation (same as sign data values)."""


class AbstractDispenser(Container):
    """A dropper or dispenser."""
    items = fields.ObjectListField('Items', item.Item)
    items.__doc__ = """Things to dispense or drop."""


class Dropper(AbstractDispenser, id='Dropper'):
    """A dropper."""
    pass


class Dispenser(AbstractDispenser, id='Trap'):
    """A dispenser."""
    pass
