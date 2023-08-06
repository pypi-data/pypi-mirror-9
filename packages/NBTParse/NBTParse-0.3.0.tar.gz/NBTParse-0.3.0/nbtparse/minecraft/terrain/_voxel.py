"""Terrain editing at the level of individual blocks.

.. note::

    This is the pure Python version of the module.  Pass ``--cython`` to
    ``setup.py`` to install the Cython version.

"""

import array
import collections
from collections import abc as cabc
import itertools
import logging
import struct
import sys
import warnings

from ...semantics import nbtobject, fields
from ... import exceptions
from . import tile

name = __name__.split('.')
name[-1] = 'voxel'
logging_name = '.'.join(name)

logger = logging.getLogger(logging_name)

del name
del logging_name


class Block:
    """A basic block, not including tile entity data.

    Blocks are not :class:`~.nbtobject.NBTObject`\ s because Minecraft does
    not store them that way.  They cannot be serialized directly to NBT.
    Instead, Minecraft stores blocks in groups called chunks.

    id is the block id, a nonnegative integer.  data is the damage value, also
    a nonnegative integer.

    Blocks compare equal if they have the same id and data.  Blocks are
    immutable and hashable.

    """
    def __init__(self, id: int, data: int=0):
        self._id = id
        self._data = data

    @property
    def id(self):
        """The block ID."""
        return self._id

    @property
    def data(self):
        """The block damage value."""
        return self._data

    def __repr__(self):
        return 'Block({!r}, {!r})'.format(self.id, self.data)

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        return self.id == other.id and self.data == other.data

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.id, self.data, type(self)))


class VoxelBuffer:
    """A 3D buffer of blocks.

    Stores block IDs and damage values in much the same way as Minecraft: a
    "packed" format involving 8-bit strings (i.e. :class:`bytearray`).

    Basic constructor will create a buffer full of air (block ID 0).

    Blocks may be retrieved or changed with standard subscription.  Slicing is
    also acceptable, and assigning a block to a slice is interpreted as
    filling the slice with the block.  However, it is not possible to resize a
    buffer once created.  Replacing a single block with subscription will
    erase the accompanying tile entity.  Slicing is a shallow copy, and will
    only duplicate references to tile entities.

    Slicing a VoxelBuffer is a potentially expensive operation.  It is linear
    in the total volume sliced, which sounds fine until we realize that the
    volume of a cube is (logically enough) cubic in the edge length.  Slices
    covering an entire VoxelBuffer are very fast, as they are optimized into a
    single memory copy.  This currently does not apply to any other slices.
    Manipulating individual blocks is relatively fast, however.

    VoxelBuffers can be iterated.  This is done in the rather esoteric YZX
    order rather than the conventional XYZ order because the former is more
    natural in practice.  The :meth:`VoxelBuffer.enumerate` method may be used
    to prepend (x, y, z) coordinates in much the same way as the builtin
    :func:`~python:enumerate` does.  Standard iteration is marginally faster
    than the following code, because it skips some unnecessary sanity checks::

        for y in range(vb.height):
            for z in range(vb.width):
                for x in range(vb.length):
                    yield vb[x, y, z]

    If you want to iterate in the XYZ ordering instead, use :meth:`xyz`.

    .. note::

       Do not write this, as it does not work::

           vb = VoxelBuffer(length, height, width)
           block = vb[x][y][z]

       Instead, write this::

           vb = VoxelBuffer(length, height, width)
           block = vb[x, y, z]

    """
    def __init__(self, length: int, height: int, width: int):
        logger.debug('Creating empty VoxelBuffer %r x %r x %r.', length,
                     height, width)
        self._length = length
        self._height = height
        self._width = width
        volume = length * width * height
        self._contents = array.array('H', b'\x00'*volume*2)
        assert len(self._contents) == volume
        self._tilemap = {}  # from relative coordinates to TileEntities
        self._observers = set()  # of callable objects

    @property
    def length(self):
        """The length (X-axis) of the buffer.

        .. note::

            This should not be confused with the :func:`len` of the buffer,
            which is the product of the length, width, and height (i.e.  the
            volume), for consistency with iteration.

        """
        return self._length

    @property
    def width(self):
        """The width (Z-axis) of the buffer."""
        return self._width

    @property
    def height(self):
        """The height (Y-axis) of the buffer."""
        return self._height

    @property
    def tilemap(self) -> cabc.MutableMapping:
        """Mutable mapping from coordinates to tile entities.

        Overwriting a single block with subscription will delete the
        corresponding entry from this mapping, even if the block is otherwise
        unchanged.  Overwriting a slice of blocks will replace the entries
        with the equivalent entries from the other buffer.

        Example code::

            vb.tilemap[(x, y, z)] = tile.TileEntity(...)

        The following is exactly equivalent and, in the opinion of the author,
        more readable::

            vb.tilemap[x, y, z] = tile.TileEntity(...)

        .. note::

            This is a mapping, not a 3D array or similar.  It cannot be sliced
            and negative indices will not be converted into positive indices.

        .. note::

            Coordinates are always relative to the origin of the VoxelBuffer,
            as with subscription.  This means they do not correspond to the
            :attr:`.TileEntity.coords` attribute.  Furthermore, said attribute
            will be ignored and overwritten with the coordinates provided to
            this mapping when the chunk is placed into a region.

        """
        return self._tilemap

    def __len__(self):
        return self.length * self.width * self.height

    def __repr__(self):
        return '<VoxelBuffer: {!r} x {!r} x {!r} blocks>'.format(self.length,
                                                                 self.height,
                                                                 self.width)

    def watch(self, observer: callable):
        """Register an observer.

        The observer will be called with three arguments every time the buffer
        is modified.  The arguments will be one of the following:

        * The (x, y, z) coordinates of the single block which has changed.
        * Three :class:`range` objects, describing the set of blocks which
          have changed (the range of X coordinates, Y coordinates, and Z
          coordinates).

        The observer must be hashable.  If this is a problem, wrap it in a
        lambda expression.

        Changes to :attr:`tilemap` will not trigger notifications.

        """
        self._observers.add(observer)

    def unwatch(self, observer: callable):
        """Unregister a previously-registered observer.

        Undoes a previous call to :meth:`watch`.  :exc:`KeyError` is raised if
        the observer was never registered.

        Observers are not automatically unregistered, so it is important to
        call this method manually if you intend the VoxelBuffer to outlive the
        observers.

        """
        self._observers.remove(observer)

    def _notify_all(self, arg_x, arg_y, arg_z):
        """Notify all observers."""
        for observer in self._observers:
            observer(arg_x, arg_y, arg_z)

    def _get_single_block(self, index: (int, int, int)) -> Block:
        """Helper function for VoxelBuffer subscription.

        Directly retrieves block number index=(x, y, z).  No slicing, no
        sanity checks.

        .. warning:: Do not invoke directly.  Instead use
           :meth:`VoxelBuffer.__getitem__`.  If non-"sane" parameters are
           passed to this function, the result is undefined behavior.
           Furthermore, this function's standards are much stricter than
           what's acceptable to :meth:`VoxelBuffer.__getitem__`.

        """
        x, y, z = index
        raw_index = (y * (self.length * self.width) + z * (self.length) + x)
        raw_data = self._contents[raw_index]
        block_id = raw_data & 0xFFF
        block_data = raw_data >> 12
        return Block(block_id, block_data)

    def _set_single_block(self, index: (int, int, int), value: Block):
        """Helper function for VoxelBuffer subscription.

        Directly replaces block number index=(x, y, z).  No slicing, no sanity
        checks.

        .. warning:: Do not invoke directly.  Instead use
           :meth:`VoxelBuffer.__setitem__`.  If non-"sane" parameters are
           passed to this function, the result is undefined behavior.
           Furthermore, this function's standards are much stricter than
           what's acceptable to :meth:`VoxelBuffer.__setitem__`.

        """
        x, y, z = index
        raw_index = (y * (self.length * self.width) + z * (self.length) + x)
        raw_data = (value.id & 0xFFF) | (value.data << 12)
        self._contents[raw_index] = raw_data
        self._tilemap.pop(index, None)

    def _fix_index(self, index: tuple) -> tuple:
        """Do basic sanitization on :obj:`index` for n-dimensional indexing.

        :obj:`index` will be converted into a tuple of integers or slice
        objects via :obj:`Ellipsis` expansion.  If this is not possible or
        :obj:`index` does not have a "sensible" value, a :exc:`TypeError` is
        raised.  Additionally, negative integers are converted into
        nonnegative integers, if all items in the tuple are integers.  If the
        tuple contains slices, all elements are converted into slices.

        """
        PROPER_INDEX_LENGTH = 3  # Number of dimensions we want to end up with
        logger.debug('Sanitizing index.')
        if index is Ellipsis:
            index = (slice(None),) * PROPER_INDEX_LENGTH
            logger.debug('Expanded "..." to %r', index)
        if type(index) is not tuple:
            raise TypeError('Index must be a tuple or "..."')
        if len(index) > PROPER_INDEX_LENGTH:
            raise TypeError('Index must be a {}-tuple or shorter.'
                            .format(PROPER_INDEX_LENGTH))
        elif len(index) < PROPER_INDEX_LENGTH:
            try:
                ellipsis_loc = index.index(Ellipsis)
                # If there is no Ellipsis, the user gave us too few items
            except ValueError as exc:
                new_exc = TypeError('Index must be expandable (via "...") '
                                    'into a {}-tuple.'
                                    .format(PROPER_INDEX_LENGTH))
                raise new_exc from exc
            before = index[:ellipsis_loc]  # Everything before the Ellipsis
            after = index[ellipsis_loc+1:]  # Everything after it
            # We only cut out one element, so:
            assert len(before) + 1 + len(after) == len(index)
            # Equivalently, len(before) + len(after) == len(index) - 1
            # By the above math, the number of slices to expand into is as
            # follows:
            middle = (slice(None),) * (PROPER_INDEX_LENGTH - (len(index) - 1))
            logger.debug('Expanded "..." to %r', middle)
            # Rebuild the index with the new slices:
            index = tuple(itertools.chain(before, middle, after))
        assert len(index) == PROPER_INDEX_LENGTH
        if not all(type(x) is int or type(x) is slice for x in index):
            raise TypeError('Index should consist of ints and slices after '
                            '"..." expansion.')
        if all(type(x) is int for x in index):
            logger.debug('Index is numeric, doing range checking.')
            x, y, z = index
            if x < 0:
                x += self.length
            if y < 0:
                y += self.height
            if z < 0:
                z += self.width
            if not (0 <= x < self.length):
                raise IndexError('X coordinate is out of range')
            if not (0 <= y < self.height):
                raise IndexError('Y coordinate is out of range')
            if not (0 <= z < self.width):
                raise IndexError('Z coordinate is out of range')
            index = (x, y, z)
        elif any(type(x) is int for x in index):
            # Convert relevant items into slices
            warnings.warn('Mixture of slices and integers in index.',
                          category=exceptions.SliceWarning, stacklevel=3)
            index = tuple(i if type(i) is slice else slice(i, i+1, None)
                          for i in index)
        logger.debug('Index sanitized to %r.', index)
        return index

    def __getitem__(self, index: tuple):
        logger.info('Retrieving index = %r from %r.', index, self)
        index = self._fix_index(index)
        if all(type(x) is int for x in index):
            logger.info('Retrieving single block %r.', index)
            return self._get_single_block(index)
        # Create a new VoxelBuffer with the required values
        logger.info('Retrieving slice %r.', index)
        if index == (slice(None), slice(None), slice(None)):
            # Special case foo[...]; let Python do the heavy lifting
            result = type(self)(self.length, self.height, self.width)
            result._contents = self._contents[:]
            return result
        x_slice, y_slice, z_slice = index
        x_range = range(*x_slice.indices(self.length))
        y_range = range(*y_slice.indices(self.height))
        z_range = range(*z_slice.indices(self.width))
        result = type(self)(len(x_range), len(y_range), len(z_range))
        for x_count, x in enumerate(x_range):
            for y_count, y in enumerate(y_range):
                for z_count, z in enumerate(z_range):
                    my_index = (x, y, z)
                    their_index = (x_count, y_count, z_count)
                    result._set_single_block(their_index,
                                             self._get_single_block(my_index))
        for (x, y, z), tile in self._tilemap.items():
            if x in x_range and y in y_range and z in z_range:
                my_index = (x, y, z)
                their_index = ((x - x_range.start) // x_range.step,
                               (y - y_range.start) // y_range.step,
                               (z - z_range.start) // z_range.step)
                result._tilemap[their_index] = tile
        return result

    def __setitem__(self, index: tuple, value):
        logger.info('Retrieving index = %r from %r.', index, self)
        index = self._fix_index(index)
        if all(type(x) is int for x in index):
            logger.info('Setting single block %r to %r.', index, value)
            if value.id < 0:
                raise ValueError('Cannot use block with negative ID')
            self._set_single_block(index, value)
            self._notify_all(*index)
            return
        logger.info('Setting slice %r to %r.', index, value)
        x_slice, y_slice, z_slice = index
        x_range = range(*x_slice.indices(self.length))
        y_range = range(*y_slice.indices(self.height))
        z_range = range(*z_slice.indices(self.width))
        if type(value) is Block:
            # Fill the slice with value
            if value.id < 0:
                raise ValueError('Cannot ues block with negative ID')
            blk = value
            volume = len(x_range) * len(y_range) * len(z_range)
            value = VoxelBuffer(len(x_range), len(y_range), len(z_range))
            raw_value = (blk.id & 0xFFF) | ((blk.data & 0xF) << 12)
            raw_data = struct.pack('H', raw_value)
            value._contents = array.array('H', raw_data*volume)
        if len(x_range) != value.length:
            raise ValueError('Cannot resize (in the X direction) via slicing')
        if len(y_range) != value.height:
            raise ValueError('Cannot resize (in the Y direction) via slicing')
        if len(z_range) != value.width:
            raise ValueError('Cannot resize (in the Z direction) via slicing')
        if index == (slice(None), slice(None), slice(None)):
            # Optimize foo[...] = bar
            self._contents = value._contents[:]
            self._notify_all(x_range, y_range, z_range)
            return
        if value is self:
            # Make a copy to guarantee sanity
            value = value[...]
        try:
            get_block = value._get_single_block
        except AttributeError:
            get_block = lambda index: value[index]
        for x_count, x in enumerate(x_range):
            for y_count, y in enumerate(y_range):
                for z_count, z in enumerate(z_range):
                    my_index = (x, y, z)
                    their_index = (x_count, y_count, z_count)
                    self._set_single_block(my_index, get_block(their_index))
        for (x, y, z), tile in list(self._tilemap.items()):
            if x in x_range and y in y_range and z in z_range:
                del self._tilemap[x, y, z]
        for (x, y, z), tile in value._tilemap.items():
            their_index = (x, y, z)
            my_index = (x_range.start + x*x_range.step,
                        y_range.start + y*y_range.step,
                        z_range.start + z*z_range.step)
            self._tilemap[my_index] = tile
        self._notify_all(x_range, y_range, z_range)

    @classmethod
    def from_raw(cls, ids: bytes, addids: bytes, damages: bytes, length: int,
                 height: int, width: int):
        """Create a new VoxelBuffer from the provided buffers.

        These buffers should be :class:`bytes` objects (or acceptable to
        :func:`bytes`).  Each byte or nybble should correspond to a block, in
        the same format as minecraft stores terrain data.

        No tile entities will be attached to the terrain.  You must do this
        manually.

        Do not use this to duplicate a VoxelBuffer.  Instead, take a slice of
        the entire buffer.

        """
        volume = length * height * width
        nybble_volume = (volume // 2) + (volume % 2)
        # Make copies and do type-checking:
        ids = bytearray(ids)
        addids = bytearray(addids)
        damages = bytearray(damages)
        if len(ids) != volume:
            raise ValueError("Wrong number of bytes in ids.")
        if len(addids) != nybble_volume:
            raise ValueError("Wrong number of bytes in addids.")
        if len(damages) != nybble_volume:
            raise ValueError("Wrong number of bytes in damages.")
        new = cls(length, height, width)
        for y in range(height):
            for z in range(width):
                for x in range(length):
                    index = y*width*length + z*length + x
                    nybble_index = index // 2
                    # Odd-numbered damage values are in the high nybble:
                    nybble_shift = 4 * (index%2)
                    block_id = ids[index]
                    add_id = addids[nybble_index] >> nybble_shift
                    add_id &= 0xF
                    block_id |= add_id << 8
                    block_data = damages[nybble_index] >> nybble_shift
                    block_data &= 0xF
                    new._set_single_block((x, y, z),
                                          Block(block_id, block_data))
        return new

    def to_raw(self) -> (bytes, bytes, bytes):
        """Return the raw buffers as used by Minecraft."""
        volume = len(self)
        nybble_volume = (volume // 2) + (volume % 2)
        base_ids = bytearray(volume)
        add_ids = bytearray(nybble_volume)
        damages = bytearray(nybble_volume)
        length = self.length
        height = self.height
        width = self.width
        for y in range(height):
            for z in range(width):
                for x in range(length):
                    index = y*width*length + z*length + x
                    nybble_index = index // 2
                    # Odd-numbered damage values are in the high nybble:
                    nybble_shift = 4 * (index%2)
                    blk = self._get_single_block((x, y, z))
                    base_id = blk.id & 0xFF
                    add_id = blk.id >> 8
                    damage = blk.damage
                    base_ids[index] = base_id
                    add_ids[nybble_index] |= add_id << nybble_shift
                    damages[nybble_index] |= damage << nybble_shift
        return bytes(base_ids), bytes(add_ids), bytes(damages)

    def enumerate(self):
        """Iterate over the blocks in the buffer, with coordinates.

        Produces the (x, y, z) coordinates of each block in addition to the
        block itself::

            for (x, y, z), block in vb.enumerate():
                # block is equivalent to vb[x, y, z]

        """
        for y in range(self.height):
            for z in range(self.width):
                for x in range(self.length):
                    yield ((x, y, z), self._get_single_block((x, y, z)))

    def xyz(self):
        """Iterate over the blocks in the buffer, in XYZ order.

        Produces coordinates, just like :meth:`VoxelBuffer.enumerate`.

        """
        for x in range(self.length):
            for y in range(self.height):
                for z in range(self.width):
                    yield ((x, y, z), self._get_single_block((x, y, z)))

    def __iter__(self):
        for _, block in self.enumerate():
            yield block

    def __reversed__(self):
        for y in reversed(range(self.height)):
            for z in reversed(range(self.width)):
                for x in reversed(range(self.length)):
                    yield self._get_single_block((x, y, z))
