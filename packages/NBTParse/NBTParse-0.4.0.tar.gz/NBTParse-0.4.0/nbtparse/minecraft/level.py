from ..syntax import tags
from ..semantics import filetype, fields, nbtobject
from . import mobs


class RulesField(fields.HomogenousDictField):
    """Field for the dictionary of game rules."""
    def item_to_python(self, key, value):
        return (str(key), value=='true')

    def item_from_python(self, key, value):
        if value:
            return (tags.StringTag(key), tags.StringTag('true'))
        else:
            return (tags.StringTag(key), tags.StringTag('false'))


class LevelFile(filetype.GzippedNBTFile):
    """Represents a ``level.dat`` file."""
    version = fields.IntField('version')
    version.__doc__ = 'The NBT version of this level; should be 19133.'
    initialized = fields.BooleanField('initialized')
    initialized.__doc__ = ('Whether world has undergone "running initial '
                           'simulation..."')
    name = fields.UnicodeField('LevelName')
    name.__doc__ = 'The name of the level.'
    generator = fields.UnicodeField('generatorName')
    generator.__doc__ = '''The name of the generator used to create the level.

                        .. note:: This is not a vanity field.  Minecraft uses
                           it to decide how to populate empty chunks.  Putting
                           an arbitrary string here may cause problems

                        '''
    generator_version = fields.IntField('generatorVersion')
    generator_version.__doc__ = 'Version number of the :obj:`generator`.'
    generator_options = fields.UnicodeField('generatorOptions')
    generator_options.__doc__ = '''Custom superflat settings.

                                Empty for other generators.'''
    seed = fields.LongField('RandomSeed')
    seed.__doc__ = '''Seed for the world generator.'''
    features = fields.BooleanField('MapFeatures')
    features.__doc__ = '''Whether or not structures are generated.'''
    last_played = fields.UTCField('LastPlayed')
    last_played.__doc__ = '''Time (in UTC) when level was last loaded.'''
    size = fields.LongField('SizeOnDisk')
    size.__doc__ = '''Estimated size of the level on disk.

                   Currently ignored by Minecraft.

                   '''
    cheats = fields.BooleanField('allowCommands')
    cheats.__doc__ = '''Whether cheats are enabled.'''
    hardcore = fields.BooleanField('hardcore')
    hardcore.__doc__ = '''Whether hardcore mode is enabled.'''
    game_type = fields.IntField('GameType')
    game_type.__doc__ = '''The game mode.'''
    ticks = fields.LongField('Time')
    ticks.__doc__ = '''Age of the level in ticks.'''
    time_of_day = fields.LongField('DayTime')
    time_of_day.__doc__ = ('Age in the level in thousandths of in-game '
                           'hours.')
    spawn = fields.TupleMultiField(('SpawnX', 'SpawnY', 'SpawnZ'),
                                   (int, int, int),
                                   (tags.IntTag, tags.IntTag, tags.IntTag),
                                   default=(0, 0, 0))
    spawn.__doc__ = "Coordinates of the level's spawn."
    raining = fields.BooleanField('raining')
    raining.__doc__ = 'Whether rain and snow are falling on the level.'
    rain_time = fields.IntField('rainTime')
    rain_time.__doc__ = 'Number of ticks until :obj:`raining` changes.'
    thundering = fields.BooleanField('thundering')
    thundering.__doc__ = 'Whether a lightning storm is happening.'
    thunder_time = fields.IntField('thunderTime')
    thunder_time.__doc__ = 'Number of ticks until :obj:`thundering` changes.'
    player = fields.NBTObjectField('Player', mobs.Player)
    player.__doc__ = '''The :obj:`player<.mobs.Player>`.

                     May not exist in multiplayer.

                     '''
    rules = RulesField('GameRules')
    rules.__doc__ = """The custom rules for this level.

    Stored as a dictionary.  Keys are rule names and values are booleans.

    """

    @staticmethod
    def prepare_save(nbt: tags.CompoundTag) -> tags.CompoundTag:
        """Wrap the argument in a singleton CompoundTag."""
        return tags.CompoundTag({'Data': nbt})

    @staticmethod
    def prepare_load(nbt: tags.CompoundTag) -> tags.CompoundTag:
        """Unwrap the argument."""
        return nbt['Data']

    def __repr__(self):
        return '<LevelFile instance: name={!r}>'.format(self.name)
