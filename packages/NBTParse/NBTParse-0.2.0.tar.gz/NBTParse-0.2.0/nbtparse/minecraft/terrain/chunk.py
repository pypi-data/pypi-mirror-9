from collections import abc as cabc
import functools
import logging

from ...syntax import tags
from ...syntax import ids
from ...semantics import fields
from ...semantics import nbtobject
from .. import entity
from .. import entityfactory
from . import tile
from . import voxel


logger = logging.getLogger(__name__)


SECTION_LENGTH = 16
SECTION_HEIGHT = 16
SECTION_WIDTH = 16

SECTIONS_PER_CHUNK = 16


class HeightMap(cabc.MutableMapping):
    """The height map of a chunk.

    Maps coordinates to heights::

        hm[3, 4] = 5

    Keys may not be inserted or deleted, and must be pairs of integers.
    Intlist should be the raw list of integers as saved by Minecraft.

    """
    def __init__(self, intlist: [int]):
        required_len = SECTION_LENGTH * SECTION_WIDTH
        if len(intlist) != required_len:
            raise ValueError('Must have exactly {} entries'
                             .format(required_len))
        self._intlist = list(intlist)

    def _fix_idx(self, idx: (int, int)) -> (int, int):
        x_idx, z_idx = idx
        if x_idx not in range(SECTION_LENGTH):
            raise IndexError('X index out of range')
        if z_idx not in range(SECTION_WIDTH):
            raise IndexError('Z index out of range')
        return idx

    def __getitem__(self, idx: (int, int)) -> int:
        x_idx, z_idx = self._fix_idx(idx)
        return self._intlist[z_idx * SECTION_LENGTH + x_idx]

    def __setitem__(self, idx: (int, int), value: int):
        x_idx, z_idx = self._fix_idx(idx)
        self._intlist[z_idx * SECTION_LENGTH + x_idx] = value

    def __delitem__(self, idx: (int, int)):
        raise TypeError('Cannot delete items.')

    def __iter__(self):
        yield from self._intlist

    def __len__(self):
        return len(self._intlist)

    def to_raw(self) -> [int]:
        """Returns the raw list used by Minecraft."""
        return list(self._intlist)


class HeightMapField(fields.MutableField, fields.SingleField):
    """Field for :class:`HeightMap`."""
    def __init__(self, nbt_name: str, *, default: HeightMap=None):
        super().__init__(nbt_name, cache_key=nbt_name, default=default)

    def __repr__(self):
        return 'HeightMapField({!r}, default={!r})'.format(self.nbt_name,
                                                           self.default)

    @staticmethod
    def to_python(tag: tags.IntArrayTag) -> HeightMap:
        return HeightMap(tag)

    @staticmethod
    def from_python(value: HeightMap) -> tags.IntArrayTag:
        return tags.IntArrayTag(value.to_raw())


class BlockField(fields.MutableField, fields.MultiField):
    """Exposes the blocks in a section.

    If default is :obj:`None`, a new empty buffer will be created as the
    default.

    """
    def __init__(self, id_name: str, addid_name: str, damage_name: str, *,
                 length: int, height: int, width: int,
                 default: voxel.VoxelBuffer=None):
        if (length * width * height) % 2 == 1:
            raise ValueError('Cannot create BlockField with odd length.')
        self.length = length
        self.height = height
        self.width = width
        nbt_names = (id_name, addid_name, damage_name)
        super().__init__(nbt_names, cache_key=nbt_names,default=default)

    def __repr__(self) -> str:
        id_name, addid_name, damage_name = self.nbt_names
        return ('BlockField({!r}, {!r}, {!r}, length={!r}, height={!r}, '
                'width={!r}, default={!r})'.format(id_name, addid_name,
                                                   damage_name, self.length,
                                                   self.height, self.width,
                                                   self.default))

    def set_default(self, obj):
        """Set this field to its default.

        If default is :obj:`None`, create a new empty
        :class:`~.voxel.VoxelBuffer`.

        """
        if self.default is None:
            default = voxel.VoxelBuffer(self.length, self.height, self.width)
            self.__set__(obj, default)
        else:
            super().set_default(self, obj)

    def to_python(self, ids: tags.ByteArrayTag, addids: tags.ByteArrayTag,
                    damages: tags.ByteArrayTag) -> voxel.VoxelBuffer:
        length = self.length
        height = self.height
        width = self.width
        if addids is None:
            addids = bytearray((length * width * height) // 2)
        return voxel.VoxelBuffer.from_raw(ids, addids, damages,
                                          length=length, height=height,
                                          width=width)

    @staticmethod
    def from_python(vb: voxel.VoxelBuffer):
        result = vb.to_raw()
        return tuple(tags.ByteArrayTag(x) for x in result)


class Section(nbtobject.NBTObject):
    y_index = fields.ByteField('Y')
    y_index.__doc__ = """The Y-index of this section.

    From 0 to 15 inclusive.

    """
    blocks = BlockField('Blocks', 'Add', 'Data', length=SECTION_LENGTH,
                        width=SECTION_WIDTH, height=SECTION_HEIGHT)
    blocks.__doc__ = """:class:`~.voxel.VoxelBuffer` of this section."""


class _MagicDict(dict):
    def __missing__(self, key):
        if key not in range(SECTIONS_PER_CHUNK):
            raise KeyError(key)
        result = Section()
        result.y_index = key
        self[key] = result
        return result

class SectionDictField(fields.MutableField, fields.SingleField):
    """Field for the sections of a chunk.

    Keys are y_index, values are sections.

    """
    def __init__(self, nbt_name: str, *, default: dict=None):
        super().__init__(nbt_name, cache_key=nbt_name, default=default)

    def __repr__(self):
        return 'SectionDictField({!r}, default={!r})'.format(self.nbt_name,
                                                             self.default)
    @staticmethod
    def to_python(sec_list: tags.ListTag) -> dict:
        result = _MagicDict()
        for raw_sec in sec_list:
            cooked_sec = Section.from_nbt(raw_sec)
            result[cooked_sec.y_index] = cooked_sec
        return result

    @staticmethod
    def from_python(sec_dict: dict) -> tags.ListTag:
        result = tags.ListTag(content_id=ids.TAG_Compound)
        for cooked_sec_y, cooked_sec in sec_dict.items():
            cooked_sec.y_index = cooked_sec_y
            raw_sec = cooked_sec.to_nbt()
            result.append(raw_sec)
        return result


class Chunk(nbtobject.NBTObject):
    sections = SectionDictField('Sections')
    sections.__doc__ = (
        """Mutable mapping from Y-indices to :class:`Section`\ s.

        Y-indices which are not present in the underlying NBT will be
        automagically created as empty sections upon attempting to retrieve
        them.

        The key in this mapping will override the :attr:`~Section.y_index`
        attribute if they disagree.

        .. note::

            It is acceptable to replace this mapping with an entirely
            different mapping.  If you do so, the magic creation of missing
            sections will very likely not work.  If you prefer creating
            sections explicitly, code like the following will disable the
            magic::

                c = Chunk.from_nbt(...)
                c.sections = dict(c.sections)

        """)
    tiles = fields.ListField('TileEntities',
                             functools.partial(entityfactory.from_nbt,
                                               default_class=tile.TileEntity),
                             lambda x: x.to_nbt(), ids.TAG_Compound)
    tiles.__doc__ = """List of :class:`~.tile.TileEntity` objects.

    .. note::

        This attribute is generally managed by the :class:`~.region.Region`
        which created this chunk.  Manually changing it is usually
        unnecessary.

    """
    entities = fields.ListField('Entities', entityfactory.from_nbt,
                                lambda x: x.to_nbt(), ids.TAG_Compound)
    entities.__doc__ = """List of :class:`~.entity.Entity` objects."""
    height_map = HeightMapField('HeightMap')
    height_map.__doc__ = """The height map for this chunk.

    .. note::

        It is planned that a lighting engine will manage this attribute
        automatically.  This is not yet implemented.

    """

    def __repr__(self):
        return '<Chunk at 0x{:x}>'.format(id(self))

    @staticmethod
    def prepare_save(nbt: tags.CompoundTag) -> tags.CompoundTag:
        """Wrap nbt in a singleton CompoundTag."""
        return tags.CompoundTag({'Level': nbt})

    @staticmethod
    def prepare_load(nbt: tags.CompoundTag) -> tags.CompoundTag:
        """Unwrap nbt from a singleton CompoundTag."""
        return nbt['Level']
