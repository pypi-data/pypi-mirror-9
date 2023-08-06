from collections import abc as cabc
import datetime as dt
import io
import itertools
import logging
import struct
import time
import zlib

from . import chunk

logger = logging.getLogger(__name__)

OFFSET_LENGTH = 4  # bytes
TIMESTAMP_LENGTH = 4

SECTOR_SIZE = 4096  # 4 KiB

CHUNK_HEADER = 5  # bytes

GZIP_COMPRESSION = 1
ZLIB_COMPRESSION = 2

SIDE_LENGTH = 32  # chunks
CHUNK_LENGTH = 16  # blocks
SECTION_HEIGHT = 16
SIDE_LENGTH_BLOCKS = SIDE_LENGTH * CHUNK_LENGTH


def _fix_index(index):
    x, z = index
    x = int(x)
    z = int(z)
    x %= SIDE_LENGTH
    z %= SIDE_LENGTH
    return (x, z)


class Region(cabc.MutableMapping):
    """A Minecraft region file.

    :obj:`region_x` and :obj:`region_z` should be the region coordinates (as
    they appear in the filename).  Standard constructor creates an empty
    region.  :meth:`load` loads a region from a file.

    For both loading and saving, files generally need to be seekable.  This
    may pose a problem if you want to send a region over the network or
    through a pipe.  Depending on your memory and disk resources, you may be
    able to use :class:`io.BytesIO` or :mod:`tempfile` as temporary buffers.

    Contains individual chunks.  Access chunk (1, 2), in chunk coordinates,
    as follows::

        r = Region.load(...)
        chunk = r[1, 2]

    No slicing.  A :exc:`KeyError` is raised if the chunk does not exist.  You
    may use absolute or relative coordinates as you please; they will be
    translated into positive relative coordinates via modulus.  You may also
    replace one chunk with another.

    """
    def __init__(self, region_x: int, region_z: int):
        filename = 'r.{}.{}.mca'.format(region_x, region_z)
        self.chunks = {}
        self.timestamps = {}
        self.coords = (region_x, region_z)

    @classmethod
    def load(cls, region_x: int, region_z: int, src: io.BufferedReader):
        """Load a region from disk (or another I/O-like object).

        :obj:`src` must support seeking in both directions.

        """
        if not src.seekable():
            raise ValueError('src must be seekable')
        result = cls(region_x, region_z)
        not_present = set()
        offsets = {}
        lengths = {}
        timestamps = {}
        for z, x in itertools.product(range(SIDE_LENGTH), repeat=2):
            logger.debug('Reading offset data for chunk %r, %r', x, z)
            raw = src.read(OFFSET_LENGTH)
            if len(raw) < OFFSET_LENGTH:
                raise RuntimeError('Incomplete region file.')
            high_word, low_byte, length = struct.unpack('>HBB', raw)
            offset = (high_word << 8) | low_byte
            if offset == 0:
                logger.debug('Chunk %r, %r is absent', x, z)
                not_present.add((x, z))
            else:
                offsets[x, z] = offset*SECTOR_SIZE
                lengths[x, z] = length*SECTOR_SIZE
        for z, x in itertools.product(range(SIDE_LENGTH), repeat=2):
            if (x, z) in not_present:
                logger.debug('Skipping timestamp for absent chunk '
                             '%r, %r', x, z)
                src.seek(TIMESTAMP_LENGTH, io.SEEK_CUR)
                continue
            logger.debug('Reading timestamp for chunk %r, %r', x, z)
            raw = src.read(TIMESTAMP_LENGTH)
            if len(raw) < TIMESTAMP_LENGTH:
                raise RuntimeError('Incomplete region file.')
            (posix_time,) = struct.unpack('>i', raw)
            timestamp = dt.datetime.fromtimestamp(posix_time,
                                                  dt.timezone.utc)
            logger.debug('Timestamp is %s', timestamp)
            result.timestamps[x, z] = timestamp
        for (x, z), offset in offsets.items():
            result._load_chunk(x, z, src, offset)
        return result

    def _load_chunk(self, x: int, z: int, src: io.BufferedReader,
                    offset: int):
        logger.debug('Loading chunk at %r, %r from %r', x, z, src)
        src.seek(offset)
        header = src.read(CHUNK_HEADER)
        length, compression = struct.unpack('>IB', header)
        compressed = src.read(length - 1)
        logger.debug('Compressed: %r bytes', len(compressed))
        if compression != ZLIB_COMPRESSION:
            raise RuntimeError('Cannot work with compression method {!r}'
                               .format(compression))
        if len(compressed) != length - 1:
            raise RuntimeError('Incomplete chunk')
        raw_chunk = zlib.decompress(compressed)
        logger.debug('Uncompressed: %r bytes', len(raw_chunk))
        loaded = chunk.Chunk.from_bytes(raw_chunk)
        self.chunks[x, z] = loaded
        self._insert_tiles(x, z)

    def __repr__(self):
        x, z = self.coords
        return '<Region at ({!r}, {!r})>'.format(x, z)

    def _extract_tiles(self):
        """Extract tile entities and prepare to save them to disk."""
        r_x, r_z = self.coords
        for (c_x, c_z), c in self.items():
            logger.debug('Extracting tile entities from VoxelBuffers in chunk'
                         ' (%i, %i)', c_x, c_z)
            # Calculate origin of the chunk
            base_x = r_x*SIDE_LENGTH_BLOCKS + c_x*CHUNK_LENGTH
            base_z = r_z*SIDE_LENGTH_BLOCKS + c_z*CHUNK_LENGTH
            c.tiles = []
            for sec_y, section in c.sections.items():
                base_y = sec_y*SECTION_HEIGHT
                # Now (base_x, base_y, base_z) is the origin of section.blocks
                tilemap = section.blocks.tilemap
                for (x, y, z), t in tilemap.items():
                    block_x = x + base_x
                    block_y = y + base_y
                    block_z = z + base_z
                    t.coords = (block_x, block_y, block_z)
                    logger.debug('Extracted tile entity at (%i, %i, %i), '
                                 'chunk coordinates (%i, %i, %i), from '
                                 'section %i', block_x, block_y, block_z, x,
                                 y, z, sec_y)
                    c.tiles.append(t)

    def _insert_tiles(self, x, z):
        """Insert tile entities into VoxelBuffers."""
        logger.debug('Inserting tile entities into VoxelBuffers in chunk (%i,'
                     ' %i)', x, z)
        result = self[x, z]
        for t in result.tiles:
            block_x, block_y, block_z = t.coords
            chunk_x = block_x % 16
            chunk_y = block_y % 16
            chunk_z = block_z % 16
            section = block_y // 16
            logger.debug('Inserting tile entity at (%i, %i, %i), chunk '
                         ' coordinates (%i, %i, %i), into section %i',
                         block_x, block_y, block_z, chunk_x, chunk_y, chunk_z,
                         section)
            vb = result.sections[section].blocks
            vb.tilemap[chunk_x, chunk_y, chunk_z] = t

    def clear(self):
        """Mark this region as empty.

        Equivalent to deleting every chunk from the region, but quite a bit
        faster.

        """
        self.chunks.clear()
        self.timestamps.clear()

    def save(self, dest: io.BufferedWriter):
        """Save the state of this region.

        :obj:`dest` must support seeking in both directions.

        """
        if not dest.seekable():
            raise ValueError('dest must be seekable')
        self._extract_tiles()
        offset_table = {}
        length_table = {}
        total_offset = 2*SECTOR_SIZE
        # Write the chunks:
        logger.info('Saving chunks')
        for (x, z), chnk in self.items():
            logger.debug('Saving chunk %r, %r at offset %r', x, z,
                         total_offset)
            # Loop invariant: total_offset % SECTOR_SIZE == 0
            assert total_offset % SECTOR_SIZE == 0
            dest.seek(total_offset)
            offset_table[x, z] = total_offset // SECTOR_SIZE
            raw_chunk = chnk.to_bytes()
            logger.debug('Uncompressed: %r bytes', len(raw_chunk))
            compressed = zlib.compress(raw_chunk)
            logger.debug('Compressed: %r bytes', len(compressed))
            length = len(compressed) + 1
            # length_table[x, z] = ceil(length / SECTOR_SIZE)
            # But that would create floating-point errors, so:
            length_table[x, z] = (length // SECTOR_SIZE)
            if length % SECTOR_SIZE != 0:
                length_table[x, z] += 1
            header = struct.pack('>IB', length, ZLIB_COMPRESSION)
            total_offset += dest.write(header)
            total_offset += dest.write(compressed)
            if total_offset % SECTOR_SIZE != 0:
                total_offset += SECTOR_SIZE - (total_offset % SECTOR_SIZE)
        dest.seek(0)
        # Now write the header:
        logger.info('Saving header')
        for z, x in itertools.product(range(SIDE_LENGTH), repeat=2):
            if (x, z) not in offset_table:
                logger.debug('Skipping missing chunk %r, %r', x, z)
                dest.write(b'\x00\x00\x00\x00')
                continue
            logger.debug('Writing header for chunk %r, %r', x, z)
            sector_offset = offset_table[x, z]
            sector_length = length_table[x, z]
            high_word = (sector_offset & 0xFFFF00) >> 8
            low_byte = sector_offset & 0xFF
            item = struct.pack('>HBB', high_word, low_byte, sector_length)
            dest.write(item)
        now = int(time.time()) & 0x7FFFFFFF
        # XXX: This will cause a Y2k38 bug, but it's Mojang's fault for
        #      using 4-byte timestamps in the first place.
        logger.info('Saving timestamps (as %r)', now)
        for z, x in itertools.product(range(SIDE_LENGTH), repeat=2):
            if (x, z) not in offset_table:
                logger.debug('Skipping missing chunk %r, %r', x, z)
                dest.write(b'\x00\x00\x00\x00')
                continue
            logger.debug('Writing timestamp for chunk %r, %r', x, z)
            item = struct.pack('>i', now)
            dest.write(item)

    def __getitem__(self, index: (int, int)) -> chunk.Chunk:
        x, z = _fix_index(index)
        return self.chunks[x, z]

    def __setitem__(self, index: (int, int), value: chunk.Chunk):
        x, z = _fix_index(index)
        self.chunks[x, z] = value

    def __delitem__(self, index: (int, int)):
        x, z = _fix_index(index)
        del self.chunks[x, z]
        del self.timestamps[x, z]

    def __iter__(self):
        for key in self.chunks.keys():
            yield key

    def __len__(self):
        return len(self.chunks)
