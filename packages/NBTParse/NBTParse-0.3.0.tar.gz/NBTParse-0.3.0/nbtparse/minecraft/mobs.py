"""All the mobs in vanilla minecraft."""

import abc
import collections
import collections.abc as cabc
import enum
import numbers

from ..syntax import tags, ids
from ..semantics import filetype, fields, nbtobject
from . import entity, item

DIM_NETHER = -1
DIM_OVERWORLD = 0
DIM_END = 1

MODE_SURVIVAL = 0
MODE_CREATIVE = 1
MODE_ADVENTURE = 2


class HealthField(fields.MultiField):
    """A field for a mob's health."""
    def __init__(self, short_name: str, float_name: str,
                 default: numbers.Real=0):

        nbt_names = (short_name, float_name)
        super(HealthField, self).__init__(nbt_names, default=0)

    def __repr__(self):
        short_name, float_name = self.nbt_names
        return 'HealthField({!r}, {!r}, default={!r})'.format(self.short_name,
                                                              self.float_name,
                                                              self.default)
    @staticmethod
    def to_python(short_tag: tags.ShortTag,
                  float_tag: tags.FloatTag) -> numbers.Real:
        if float_tag is not None:
            return float(float_tag)
        elif short_tag is None:
            return None
        else:
            return int(short_tag)

    @staticmethod
    def from_python(value: numbers.Real) -> (tags.ShortTag, tags.FloatTag):
        if isinstance(value, numbers.Integral):
            return (tags.ShortTag(value), tags.FloatTag(value))
        elif isinstance(value, numbers.Real):
            return (None, tags.FloatTag(value))
        else:
            raise TypeError("Must be a real number.")


class PotionEffect(nbtobject.NBTObject):
    """A potion effect, usually attached to a mob."""
    id = fields.ByteField('id')
    amplifier = fields.ByteField('Amplifier')
    duration = fields.IntField('Duration')
    ambient = fields.BooleanField('Ambient')

    def __repr__(self):
        return 'PotionEffect.from_nbt({!r})'.format(self.data)


class Modifier(nbtobject.NBTObject):
    """An attribute modifier."""
    name = fields.UnicodeField('Name')
    amount = fields.DoubleField('Amount')
    operation = fields.IntField('Operation')
    uuid = fields.UUIDField('UUIDMost', 'UUIDLeast')

    def __repr__(self):
        return 'Modifier.from_nbt({!r})'.format(self.data)


class Attribute(nbtobject.NBTObject):
    """An attribute, usually attached to a mob."""
    name = fields.UnicodeField('Name')
    base = fields.DoubleField('Base')
    modifiers = fields.ObjectListField('Modifiers', Modifier)

    def __repr__(self):
        return '<Attribute: name={!r}, base={!r}>'.format(self.name,
                                                          self.base)


class Leash(nbtobject.NBTObject):
    """A leash for a mob.

    Only represents one "end" of the leash

    Exactly one of uuid and coords should exist.
    """
    uuid = fields.UUIDField('UUIDMost', 'UUIDLeast')
    coords = fields.TupleMultiField(('X', 'Y', 'Z'), (int,) * 3,
                                    (tags.IntTag,) * 3, default=(0,) * 3)

    def __repr__(self):
        return '<Leash: uuid={!r}, coords={!r}>'.format(self.uuid,
                                                        self.coords)


class Mob(entity.Entity):
    """A mob, in minecraft terms.

    Do not instantiate directly, instead use a subclass.
    """
    health = HealthField('Health', 'HealthF')
    absorption = fields.FloatField('AbsorptionAmount')
    attack_ticks = fields.ShortField('AttackTime')
    hurt_ticks = fields.ShortField('HurtTime')
    death_ticks = fields.ShortField('DeathTime')
    attributes = fields.ObjectListField('Attributes', Attribute)
    active_effects = fields.ObjectListField('ActiveEffects', PotionEffect)
    equipment = fields.ObjectTupleField('Equipment', item.Item)
    drop_chances = fields.TupleListField('DropChances', float, tags.FloatTag,
                                         ids.TAG_Float, default=(0.0,)*5)
    can_pickup_loot = fields.BooleanField('CanPickUpLoot')
    persistent = fields.BooleanField('PersistenceRequired')
    name = fields.UnicodeField('CustomName')
    name_visible = fields.BooleanField('CustomNameVisible')
    leashed = fields.BooleanField('Leashed')
    leash = fields.NBTObjectField('Leash', Leash)


class Breedable(Mob):
    """A mob which can be bred."""
    in_love = fields.IntField('InLove')
    age = fields.IntField('Age')


class Tameable(Mob):
    """A mob which can be tamed.

    Horses are not tamed conventionally and are not Tameable.
    """
    owner = fields.UnicodeField('Owner')
    sitting = fields.BooleanField('Sitting')


class Blaze(Mob, id='Blaze'):
    """A blaze.

    Flying ranged mob that shoots fire.

    """
    pass


class Creeper(Mob, id='Creeper'):
    """The infamous creeper.

    A 2-block tall hostile mob with an explosive attack that destroys blocks.

    """
    powered = fields.BooleanField('powered')
    explosion_radius = fields.ByteField('ExplosionRadius')
    fuse = fields.ShortField('Fuse')


class CaveSpider(Mob, id='CaveSpider'):
    """A cave spider.

    A small poisonous spider.

    """
    pass


class EnderDragon(Mob, id='EnderDragon'):
    """The Ender Dragon.

    The final boss.

    """
    pass


class Ghast(Mob, id='Ghast'):
    """A ghast.

    A large floating mob that shoots fireballs and breaks blocks.

    """
    pass


class Giant(Mob, id='Giant'):
    """A giant.

    A very large zombie.

    Doesn't spawn naturally.

    """
    pass


class Slime(Mob, id='Slime'):
    """A slime.

    A variable-sized mob which divides on death.

    """
    size = fields.IntField('Size')


class MagmaCube(Slime, id='LavaSlime'):
    """A magma cube.

    A slime from The Nether.

    """
    pass


class Silverfish(Mob, id='Silverfish'):
    """A silverfish.

    Small swarming mob that hides in tile entities.

    """
    pass


class Skeleton(Mob, id='Skeleton'):
    """A skeleton.

    A ranged mob with a bow and arrows.

    """
    wither = fields.BooleanField('SkeletonType')


class Spider(Mob, id='Spider'):
    """A spider.

    A large short mob that can climb walls.

    """
    pass


class Witch(Mob, id='Witch'):
    """A witch.

    A ranged mob that throws potions.

    """
    pass


class Wither(Mob, id='WitherBoss'):
    """A wither.

    A boss mob the player has to construct from wither skeletons.

    """
    invulnerable = fields.IntField('Invul')


class Zombie(Mob, id='Zombie'):
    """A zombie.

    A mob that can convert villagers into more zombies.

    """
    is_villager = fields.BooleanField('IsVillager')
    is_baby = fields.BooleanField('IsBaby')
    conversion_time = fields.IntField('ConversionTime')


class Enderman(Mob, id='Enderman'):
    """An enderman.

    Endermen are 3-block tall neutral mobs that can carry blocks around.
    """
    carried = fields.ShortField('carried')
    carried_data = fields.ShortField('carriedData')


class Wolf(Breedable, Tameable, id='Wolf'):
    angry = fields.BooleanField('Angry')
    collar_color = fields.ByteField('CollarColor')


class ZombiePigman(Zombie, id='PigZombie'):
    anger = fields.ShortField('Anger')


class Bat(Mob, id='Bat'):
    """A bat.

    A small flying mob.  Drops nothing.

    """
    hanging = fields.BooleanField('BatFlags')


class Chicken(Breedable, id='Chicken'):
    """A chicken.

    Small mob.  Lays eggs and drops feathers.

    """
    pass


class Cow(Breedable, id='Cow'):
    """A cow.

    Large mob.  Produces milk.  Drops leather and beef.

    """
    pass


class Mooshroom(Breedable, id='MushroomCow'):
    """A Mooshroom (mushroom-cow)

    Like the cow, but produces mushroom stew instead of milk.  Can be shorn
    into a regular cow, dropping mushrooms.

    """
    pass


@enum.unique
class HorseType(enum.Enum):
    """The valid values for :obj:`Horse.type`."""
    horse = 0  #: Indicates a regular horse.
    donkey = 1  #: Indicates a donkey.
    mule = 2  #: Indicates a mule.
    zombie = 3  #: Indicates a zombie horse; not naturally spawned.
    skeleton = 4  #: Indicates a skeleton horse; not naturally spawned.


class Horse(Breedable, id='EntityHorse'):
    """A horse.

    A tall rideable mob.

    """
    bred = fields.BooleanField('Bred')
    chested = fields.BooleanField('ChestedHorse')
    eating = fields.BooleanField('EatingHaystack')
    has_reproduced = fields.BooleanField('HasReproduced')
    tame = fields.BooleanField('Tame')
    temper = fields.IntField('Temper')
    type = fields.EnumField('Type', HorseType, default=HorseType.horse)
    variant = fields.IntField('Variant')
    owner_name = fields.UnicodeField('OwnerName')
    items = fields.ObjectListField('Items', item.Item)
    armor = fields.NBTObjectField('ArmorItem', item.Item)
    saddle = fields.NBTObjectField('SaddleItem', item.Item)


class Ocelot(Tameable, Breedable, id='Ozelot'):
    """An ocelot.

    A tameable mob.

    """
    cat_type = fields.IntField('CatType')


class Pig(Breedable, id='Pig'):
    """A pig.

    A short mob that drops porkchops.

    """
    saddle = fields.BooleanField('Saddle')


class Sheep(Breedable, id='Sheep'):
    """A sheep.

    A mob that can be shorn for wool.

    """
    sheared = fields.BooleanField('Sheared')
    color = fields.ByteField('Color')


class Squid(Mob, id='Squid'):
    """A squid.

    An underwater mob that drops ink sacs.

    """
    pass


class OfferListMeta(nbtobject.NBTMeta, abc.ABCMeta):
    """Metaclass for :class:`OfferList`."""
    pass


class Offer(nbtobject.NBTObject):
    """An individual villager offer."""
    max_uses = fields.IntField('maxUses')
    uses = fields.IntField('uses')
    buy = fields.NBTObjectField('buy', item.Item)
    buy_secondary = fields.NBTObjectField('buyB', item.Item)
    sell = fields.NBTObjectField('sell', item.Item)

    def __repr__(self):
        return ('<Offer: buy={!r}, secondary={!r}, sell={!r}>'
                .format(self.buy, self.secondary, self.sell))


class OfferList(nbtobject.NBTObject, cabc.MutableSequence,
                metaclass=OfferListMeta):
    """List of offers a villager has.

    For convenience, sequence-related functionality is redirected to
    self.recipes.

    """
    recipes = fields.ObjectListField('Recipes', Offer)

    def __getitem__(self, index):
        return self.recipes[index]

    def __setitem__(self, index, value):
        self.recipes[index] = value

    def __delitem__(self, index, value):
        del self.recipes[index]

    def insert(self, index, value):
        self.recipes.insert(index, value)

    def __len__(self):
        return len(self.recipes)


@enum.unique
class VillagerProfession(enum.Enum):
    """The valid values for :obj:`Villager.profession`."""
    farmer = 0  #: A farmer, with a brown robe.
    librarian = 1  #: A librarian, with a white robe.
    priest = 2  #: A priest, with a purple robe.
    smith = 3  #: A blacksmith, with a black apron.
    butcher = 4  #: A butcher, with a white apron.
    #: A "generic" villager, with a green robe.  Not spawned naturally.
    generic = 5


class Villager(Breedable, id='Villager'):
    """A villager.

    A passive mob that players can trade with.
    """
    profession = fields.EnumField('Profession', VillagerProfession)
    riches = fields.IntField('Riches')
    offers = fields.NBTObjectField('Offers', OfferList)


class Abilities(nbtobject.NBTObject):
    """A set of abilities for a player."""
    walk_speed = fields.FloatField('walkSpeed')
    fly_speed = fields.FloatField('flySpeed')
    may_fly = fields.BooleanField('mayfly')
    flying = fields.BooleanField('flying')
    invulnerable = fields.BooleanField('invulnerable')
    may_build = fields.BooleanField('mayBuild')
    instabuild = fields.BooleanField('instabuild')

    def __repr__(self):
        return 'Abilities.from_nbt({!r})'.format(self.data)


class Player(Mob, filetype.GzippedNBTFile):
    """A player, and the accompanying player.dat file."""
    dimension = fields.IntField('Dimension')
    mode = fields.IntField('playerGameType')
    score = fields.IntField('Score')
    selected_item_slot = fields.IntField('SelectedItemSlot')
    spawn = fields.TupleMultiField(('SpawnX', 'SpawnY', 'SpawnZ'),
                                   (int,) * 3, (tags.IntTag,) * 3,
                                   default=(0,) * 3)
    spawn_forced = fields.BooleanField('SpawnForced')
    sleeping = fields.BooleanField('Sleeping')
    sleep_timer = fields.ShortField('SleepTimer')
    food_level = fields.IntField('foodLevel')
    food_exhaustion = fields.IntField('foodExhaustionLevel')
    food_saturation = fields.IntField('foodSaturationLevel')
    food_timer = fields.IntField('foodTickTimer')
    xp_level = fields.IntField('XpLevel')
    xp_progress = fields.IntField('XpP')
    xp_total = fields.IntField('XpTotal')
    inventory = fields.ObjectListField('Inventory', item.Item)
    ender_items = fields.ObjectListField('EnderItems', item.Item)
    abilities = fields.NBTObjectField('abilities', Abilities)


class SnowGolem(Mob, id='SnowMan'):
    """A snow golem (snowman).

    A mob that throws snowballs at hostile mobs.

    """
    pass


class IronGolem(Mob, id='VillagerGolem'):
    """An iron golem.

    A large defensive mob that also spawns naturally to protect villages.

    """
    player_created = fields.BooleanField('PlayerCreated')
