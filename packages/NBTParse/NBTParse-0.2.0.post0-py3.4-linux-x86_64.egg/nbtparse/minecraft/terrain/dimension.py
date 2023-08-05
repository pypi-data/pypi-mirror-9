import collections
import collections.abc as cabc
import contextlib
import errno
import functools
import itertools
import logging
import os
import pathlib

from ...exceptions import ConcurrentError
from .. import entity
from .. import entityfactory
from . import voxel
from . import region
from . import chunk


logger = logging.getLogger(__name__)


CHUNK_BLOCKS = 16  # to a side
REGION_CHUNKS = 32  # to a side
REGION_BLOCKS = CHUNK_BLOCKS * REGION_CHUNKS

SECTIONS_PER_CHUNK = 16

HEIGHT_LIMIT = SECTIONS_PER_CHUNK * CHUNK_BLOCKS

FIRST_DOTFILE = '.phase1-inprogress'
SECOND_DOTFILE = '.phase2-inprogress'

TMP_FORMAT = 'r.{}.{}.mca.tmp'

TMP_GLOB = '*.mca.tmp'

REGION_FORMAT = 'r.{}.{}.mca'


try:
    fsync = os.fdatasync
except AttributeError:
    fsync = os.fsync


def _cache_correct(meth):
    """Decorator for public-facing methods which may enlarge the cache.

    Automatically flush the cache when the method returns.

    """
    @functools.wraps(meth)
    def wrapper(self, *args, **kwargs):
        try:
            return meth(self, *args, **kwargs)
        finally:
            self._flush_cache()
    return wrapper


class Dimension:
    """A dimension, in Minecraft terms.

    A collection of (usually) contiguous regions.

    May be indexed and sliced using block coordinates.  Indexing is similar to
    that of :class:`.voxel.VoxelBuffer`, except that X and Z coordinates are
    absolute, and X and Z slices must have both a start and an end.

    Dimensions are not thread-safe.

    """
    def __init__(self, path: str, *, max_cache: int=5,
                 fill_value: voxel.Block=None):
        #: Path to the dimension directory
        self.path = pathlib.Path(path).resolve()
        #: Value to fill in when slicing into missing regions or chunks
        self.fill_value = fill_value
        self._region_manager = _RegionManager(self, max_cache)

    def save_all(self):
        """Save every region currently cached.

        Regions which are no longer cached have already been saved.

        Prefer correctness over speed; provide the same guarantees as
        :obj:`Dimension.atomic`.

        A :exc:`~.exceptions.ConcurrentError` is raised if another save
        appears to have been in progress when this method was called.  Under
        no circumstances are two or more :meth:`save_all` calls allowed to run
        concurrently on the same directory; all but one will always fail with
        an exception.

        If an exception is raised under other circumstances, it is recommended
        to call :meth:`recover_atomic`.

        """
        self._region_manager.save_all()

    def save_fast(self):
        """Save every region currently cached (like :meth:`save_all`).

        Prefer speed over correctness; do not provide any guarantees beyond
        those of the basic region caching system.

        """
        if self._region_manager._atomic:
            raise RuntimeError('Cannot save_fast() inside an atomic block.')
        old_max = self.max_cache
        self.max_cache = 0
        self.max_cache = old_max

    @property
    def atomic(self):
        """Make the following operations atomic.

        Either every change made within the block will be saved to disk, or
        none of those changes are saved to disk.  This should not be confused
        with the other three `ACID`_ guarantees (particularly isolation).  The
        transaction is aborted if and only if an exception is raised (but see
        below).

        .. _ACID: http://en.wikipedia.org/wiki/ACID

        Can be used as a context manager or decorator::

            @dim.atomic
            def atomic_function():
                # Things in here will happen atomically.

            with dim.atomic:
                # Things in here will happen atomically

        In some circumstances, you may need to call :meth:`recover_atomic`.
        This is generally only necessary if the system crashed or lost power
        while actually saving regions to disk.  The method may roll back a
        partially-committed transaction to ensure atomicity, or it may complete
        the transaction.

        It is legal to call :meth:`save_all` while in this context.  Doing so
        creates a sort of "checkpoint"; if an exception is raised, the context
        rolls back to the last checkpoint.  There is an implicit checkpoint at
        the beginning of the context.

        Nested invocations are legal but have no effect.

        This consumes memory more aggressively than normal operations.  It
        ignores the :attr:`max_cache` attribute for the sake of correctness.

        .. warning::

            This is not the same as thread safety.  If you require thread
            safety, use explicit locking.  Multiple threads attempting to
            enter or exit the atomic context at the same time can cause data
            corruption, and the rest of the class is similarly unsafe for
            concurrent access.

        .. note::

            Atomicity is only guaranteed on systems where :func:`os.replace`
            is atomic and :func:`os.fsync` can be used on a directory.  Most
            POSIX-compliant systems should satisfy these requirements.
            Windows most likely fails the second and perhaps the first as
            well.

        """
        return self._region_manager.atomic

    def recover_atomic(self) -> bool:
        """Recover from a failure during :attr:`atomic` or :meth:`save_all`.

        Call this method if a system crash or other severe problem occurs
        while exiting an :attr:`atomic` block.  It is not necessary to call
        this method if the crash occurred while control was still inside the
        block.  The method should also be called if :meth:`save_all` raised an
        exception, even if it did so inside an atomic block.

        Return True if the changes were saved, False if the changes were
        rolled back.  Also return True if the Dimension is already in a
        "clean" state and recovery is unnecessary.

        .. warning::

            Do not call this method while a save is in progress.  Doing so
            will likely cause severe data corruption.  This rule applies
            regardless of which process is performing the save.
            :meth:`save_all` raises a :exc:`~.exceptions.ConcurrentError` to
            indicate that it believes a save cannot be safely made at the
            current time.  Calling this method will override that safety
            check.

        """
        return self._region_manager.recover_atomic()
        
    @property
    def max_cache(self):
        """The maximum number of regions to keep cached at once.

        If zero, no regions will be cached; every lookup will hit the disk.

        .. note::

            Even if this is zero, some regions will be cached for short
            periods of time during slicing operations.  This is because slice
            assignment may need to hit multiple regions at once.  The cache
            size will also be unrestricted by this parameter while inside a
            :attr:`Dimension.atomic` invocation.

        If -1, the cache size is unlimited; once a region has been loaded, it
        will not be unloaded.

        """
        return self._region_manager.max_cache

    @max_cache.setter
    def max_cache(self, new_max_cache: int):
        self._region_manager.max_cache = new_max_cache

    def _flush_cache(self, save=True):
        """Remove extraneous items from the cache.

        Bring the cache size down to :obj:`max_cache`.  Also invalidates any
        regions discarded from the cache, so use with care.  If save is False,
        regions are not saved; this should only be used if you have saved them
        by hand somewhere else.

        """
        self._region_manager.flush_cache()

    @property
    def cache_size(self):
        """Number of regions currently cached.

        Should always be <= :obj:`max_cache`, except inside a
        :attr:`Dimension.atomic` invocation.

        """
        return self._region_manager.cache_size

    def _getregion(self, r_x: int, r_z: int) -> region.Region:
        """Retrieve and return the region r_x, r_z.

        Region will be cached; you are responsible for flushing the cache when
        it is no longer needed.

        """
        return self._region_manager.get_region(r_x, r_z)

    def _getchunk(self, c_x: int, c_z: int) -> chunk.Chunk:
        """Retrieve and return the chunk c_x, c_z.

        You must flush the cache after.

        """
        r_x = c_x // REGION_CHUNKS
        r_z = c_z // REGION_CHUNKS
        r = self._getregion(r_x, r_z)
        try:
            return r[c_x, c_z]
        except KeyError as exc:
            if self.fill_value is None:
                raise IndexError('Chunk {}, {} does not exist'
                                 .format(c_x, c_z)) from exc
            logger.info('Chunk %d, %d does not exist, filling in %r', c_x,
                        c_z, self.fill_value)
            cnk = chunk.Chunk()
            for y in range(SECTIONS_PER_CHUNK):
                sec = chunk.Section()
                sec.blocks[...] = self.fill_value
                cnk.sections[y] = sec
            r[c_x, c_z] = cnk
            return cnk

    def _getsection(self, s_x: int, s_y: int, s_z: int) -> chunk.Section:
        """Retrieve and return the section s_y in chunk s_x, s_z.

        You must flush the cache after.

        """
        c = self._getchunk(s_x, s_z)
        return c.sections[s_y]

    def _getsection_byblock(self, b_x: int, b_y: int,
                            b_z: int) -> chunk.Section:
        """Same as _getsection, but use block coordinates."""
        c_x = b_x // CHUNK_BLOCKS
        c_y = b_y // CHUNK_BLOCKS
        c_z = b_z // CHUNK_BLOCKS
        s = self._getsection(c_x, c_y, c_z)
        return s

    def _getblock(self, b_x: int, b_y: int, b_z: int) -> voxel.Block:
        """Retrieve and return a single block.

        You must flush the cache.

        """
        s = self._getsection_byblock(b_x, b_y, b_z)
        x = b_x % CHUNK_BLOCKS
        y = b_y % CHUNK_BLOCKS
        z = b_z % CHUNK_BLOCKS
        return s.blocks[x, y, z]

    def _setblock(self, b_x: int, b_y: int, b_z: int, value: voxel.Block):
        """Replace a single block.

        You must flush the cache.

        """
        s = self._getsection_byblock(b_x, b_y, b_z)
        x = b_x % CHUNK_BLOCKS
        y = b_y % CHUNK_BLOCKS
        z = b_z % CHUNK_BLOCKS
        s.blocks[x, y, z] = value

    def _make_chunk_range(self, x_slice: slice, y_slice: slice,
                          z_slice: slice) -> (range, range, range):
        # Simplify the slice into one with a step of +1
        # Caller can compute the real slice later
        x_start = min(x_slice.start, x_slice.stop)
        y_start = min(y_slice.start, y_slice.stop)
        z_start = min(z_slice.start, z_slice.stop)
        x_stop = max(x_slice.start, x_slice.stop)
        y_stop = max(y_slice.start, y_slice.stop)
        z_stop = max(z_slice.start, z_slice.stop)

        # Make ranges for the affected chunks
        x_chunk_range = range(x_start // CHUNK_BLOCKS,
                              x_stop // CHUNK_BLOCKS +
                              # Round up if there's a remainder:
                              (1 if x_stop % CHUNK_BLOCKS else 0))
        y_chunk_range = range(y_start // CHUNK_BLOCKS,
                              y_stop // CHUNK_BLOCKS +
                              (1 if y_stop % CHUNK_BLOCKS else 0))
        z_chunk_range = range(z_start // CHUNK_BLOCKS,
                              z_stop // CHUNK_BLOCKS +
                              (1 if z_stop % CHUNK_BLOCKS else 0))
        return (x_chunk_range, y_chunk_range, z_chunk_range)

    def _get_chunk_slice(self, x_chunk_range: range, y_chunk_range: range,
                         z_chunk_range: range) -> voxel.VoxelBuffer:
        """Obtain a VoxelBuffer of the chunks around the given slices."""
        # Prepare a temporary buffer to hold all the chunks we need
        x_size = len(x_chunk_range) * CHUNK_BLOCKS
        y_size = len(y_chunk_range) * CHUNK_BLOCKS
        z_size = len(z_chunk_range) * CHUNK_BLOCKS
        vb = voxel.VoxelBuffer(x_size, y_size, z_size)

        # Figure out the origin of the buffer
        x_base_chunk = x_chunk_range.start
        y_base_chunk = y_chunk_range.start
        z_base_chunk = z_chunk_range.start

        # Grab all the required sections into vb
        product = itertools.product(x_chunk_range, y_chunk_range,
                                    z_chunk_range)
        for x_chunk, y_chunk, z_chunk in product:
            sec = self._getsection(x_chunk, y_chunk, z_chunk)
            x_start = (x_chunk - x_base_chunk)*CHUNK_BLOCKS
            y_start = (y_chunk - y_base_chunk)*CHUNK_BLOCKS
            z_start = (z_chunk - z_base_chunk)*CHUNK_BLOCKS
            x_stop = x_start + CHUNK_BLOCKS
            y_stop = y_start + CHUNK_BLOCKS
            z_stop = z_start + CHUNK_BLOCKS
            vb[x_start:x_stop,
               y_start:y_stop,
               z_start:z_stop] = sec.blocks

        return vb

    def _set_chunk_slice(self, x_chunk_range: range, y_chunk_range: range,
                         z_chunk_range: range, vb: voxel.VoxelBuffer):
        # Figure out the origin of the buffer
        x_base_chunk = x_chunk_range.start
        y_base_chunk = y_chunk_range.start
        z_base_chunk = z_chunk_range.start

        # For every section:
        product = itertools.product(x_chunk_range, y_chunk_range,
                                    z_chunk_range)
        for x_chunk, y_chunk, z_chunk in product:
            sec = self._getsection(x_chunk, y_chunk, z_chunk)
            x_start = (x_chunk - x_base_chunk)*CHUNK_BLOCKS
            y_start = (y_chunk - y_base_chunk)*CHUNK_BLOCKS
            z_start = (z_chunk - z_base_chunk)*CHUNK_BLOCKS
            x_stop = x_start + CHUNK_BLOCKS
            y_stop = y_start + CHUNK_BLOCKS
            z_stop = z_start + CHUNK_BLOCKS
            sec.blocks[...] = vb[x_start:x_stop, y_start:y_stop,
                                 z_start:z_stop]

    def _slice_cleanup(self, x_slice: slice, y_slice: slice,
                       z_slice: slice) -> (slice, slice, slice):
        # Y is special because of the height limit
        # Allow negatives and wraparound
        y_slice = slice(*y_slice.indices(HEIGHT_LIMIT))

        # Fill in missing steps
        if x_slice.step is None:
            x_slice = slice(x_slice.start, x_slice.stop, 1)
        if z_slice.step is None:
            z_slice = slice(z_slice.start, z_slice.stop, 1)
        index = (x_slice, y_slice, z_slice)
        if any(x.step == 0 for x in index):
            raise ValueError('Step cannot be zero')
        if any(x.start is None or x.stop is None for x in index):
            raise ValueError('Indefinite slices not allowed')
        return x_slice, y_slice, z_slice

    @_cache_correct
    def __getitem__(self, index: (slice, slice, slice)):
        if type(index) is not tuple or len(index) != 3:
            raise TypeError('Indexing is three-dimensional')
        if all(type(x) is int for x in index):
            x, y, z = index
            logger.info('Retrieving single block %r, %r, %r', x, y, z)
            return self._getblock(x, y, z)
        elif all(type(x) is slice for x in index):
            x_slice, y_slice, z_slice = self._slice_cleanup(*index)
            logger.info('Slicing dimension to %r, %r, %r',
                        x_slice, y_slice, z_slice)

            x_range, y_range, z_range = self._make_chunk_range(x_slice,
                                                               y_slice,
                                                               z_slice)

            # Obtain the chunk slice:
            vb = self._get_chunk_slice(x_range, y_range, z_range)

            x_base_chunk = x_range.start
            y_base_chunk = y_range.start
            z_base_chunk = z_range.start

            # Finally, take a slice out of vb
            # Transform the given absolute coordinates into relative
            # coordinates:
            x_start = x_slice.start - x_base_chunk*CHUNK_BLOCKS
            x_stop = x_slice.stop - x_base_chunk*CHUNK_BLOCKS
            x_step = x_slice.step
            y_start = y_slice.start - y_base_chunk*CHUNK_BLOCKS
            y_stop = y_slice.stop - y_base_chunk*CHUNK_BLOCKS
            y_step = y_slice.step
            z_start = z_slice.start - z_base_chunk*CHUNK_BLOCKS
            z_stop = z_slice.stop - z_base_chunk*CHUNK_BLOCKS
            z_step = z_slice.step

            return vb[x_start:x_stop:x_step, y_start:y_stop:y_step,
                      z_start:z_stop:z_step]

        else:
            raise TypeError('Must use slices or indices and not a '
                            'combination of both')

    @_cache_correct
    def __setitem__(self, index: (slice, slice, slice), value):
        if type(index) is not tuple or len(index) != 3:
            raise TypeError('Indexing is three-dimensional')
        if all(type(x) is int for x in index):
            if type(value) is not voxel.Block:
                raise TypeError('Individual elements must be Block, not '
                                '{}'.format(type(value).__name__))
            x, y, z = index
            self._setblock(x, y, z, value)
        elif all(type(x) is slice for x in index):
            if type(value) is not voxel.VoxelBuffer:
                raise TypeError('Slice assignment must be VoxelBuffer, not '
                                '{}'.format(type(value).__name__))
            x_slice, y_slice, z_slice = self._slice_cleanup(*index)

            x_range, y_range, z_range = self._make_chunk_range(x_slice,
                                                               y_slice,
                                                               z_slice)

            # Obtain the chunk slice:
            vb = self._get_chunk_slice(x_range, y_range, z_range)

            x_base_chunk = x_range.start
            y_base_chunk = y_range.start
            z_base_chunk = z_range.start

            # Finally, put a slice into vb
            # Transform the given absolute coordinates into relative
            # coordinates:
            x_start = x_slice.start - x_base_chunk*CHUNK_BLOCKS
            x_stop = x_slice.stop - x_base_chunk*CHUNK_BLOCKS
            x_step = x_slice.step
            y_start = y_slice.start - y_base_chunk*CHUNK_BLOCKS
            y_stop = y_slice.stop - y_base_chunk*CHUNK_BLOCKS
            y_step = y_slice.step
            z_start = z_slice.start - z_base_chunk*CHUNK_BLOCKS
            z_stop = z_slice.stop - z_base_chunk*CHUNK_BLOCKS
            z_step = z_slice.step

            vb[x_start:x_stop:x_step, y_start:y_stop:y_step,
               z_start:z_stop:z_step] = value
            self._set_chunk_slice(x_range, y_range, z_range, vb)
        else:
            raise TypeError('Must use slices or indices and not a '
                            'combination of both')

    @property
    def entities(self):
        """Sliceable collection of entities.

        Provides a similar slicing API to the dimension itself, except that
        extended slicing and ordinary indexing are unsupported.  Slicing the
        object returns a set of entities.  Slices may also be assigned to and
        deleted.  As with dimensions, all slices must be fully-qualified,
        except for Y-dimension slices.  Unlike with dimensions, slice indices
        may be fractional.

        Other collection-related operations are not currently supported.

        .. note::

            The slices are sets, not lists.  Duplicate entities with the same
            UUID and type are not supported and will be silently coalesced.

        """
        return _EntitySliceable(self)


class _RegionManager:
    """Helper class to manage region files.

    This class is primarily responsible for I/O, while the main Dimension class
    is responsible for slicing and merging regions into VoxelBuffers.

    """
    def __init__(self, owner: Dimension, max_cache: int):
        self.owner = owner
        self.regions = collections.OrderedDict()
        self._max_cache = max_cache
        self._atomic = False

    @property
    def path(self):
        return self.owner.path

    @property
    def fill_value(self):
        return self.owner.fill_value

    def _sync_directory(self):
        if os.name == 'nt':
            # This does not work on NT
            logger.debug('Skip fsync() of directory %s (because Windows)',
                         self.path)
            return
        path = str(self.path)
        fd = os.open(path, os.O_RDONLY)
        try:
            logger.debug('fsync() directory %s', self.path)
            fsync(fd)
        finally:
            os.close(fd)

    def save_all(self):
        """See :meth:`Dimension.save_all`."""
        # Do a two-phase commit
        # Touch dotfiles to mark which phase of commit we're in.
        phase_1_path = self.path / FIRST_DOTFILE
        phase_2_path = self.path / SECOND_DOTFILE

        try:
            phase_1_path.touch(exist_ok=False)
        except FileExistsError as exc:
            raise ConcurrentError('Dimension directory is dirty') from exc
        self._sync_directory()

        # Phase 1: save all regions to temporary files.
        # If this fails, we can just remove them
        for region in self.regions.values():
            tmp_path = (self.path /
                        TMP_FORMAT.format(*region.coords))
            with tmp_path.open(mode='wb') as tmp_file:
                region.save(tmp_file)
                tmp_file.flush()
                fsync(tmp_file.fileno())

        # Don't need exist_ok since we created the phase 1 file
        # If someone else left the phase 2 file behind, they were done anyway
        phase_2_path.touch()
        # The phase 1 dotfile is left in place so other processes attempting
        # to interact with the dimension using this code will fail to create
        # the file
        self._sync_directory()

        # Phase 2: Move the temporary files over the originals
        # If this fails, we can just do the rest of the moves
        for region in self.regions.values():
            tmp_path = self.path / TMP_FORMAT.format(*region.coords)
            perm_path = tmp_path.parent / REGION_FORMAT.format(*region.coords)
            tmp_path.replace(perm_path)
        self._sync_directory()

        # Remove the phase 1 dotfile first so a failure between removals
        # leaves directory in a unique state
        phase_1_path.unlink()
        self._sync_directory()
        phase_2_path.unlink()
        # It's OK if the phase 2 dotfile doesn't get removed immediately.
        # sync'ing the directory is used for happens-before, not for proper
        # durability.

    @property
    def atomic(self):
        """See :attr:`Dimension.atomic`."""
        return _AtomicContext(self)

    def recover_atomic(self) -> bool:
        """See :meth:`Dimension.recover_atomic`."""
        phase_1_path = self.path / FIRST_DOTFILE
        phase_2_path = self.path / SECOND_DOTFILE
        phase_1_exists = phase_1_path.exists()
        phase_2_exists = phase_2_path.exists()
        logger.info('Repairing failed save_all()')
        if phase_1_exists and phase_2_exists:
            # We were in phase 2.  Just finish it.
            logger.info('Completing save')
            tmpfile_glob = self.path.glob(TMP_GLOB)
            for source in tmpfile_glob:
                # Slice off the '.tmp' extension, leaving the '.mca'
                destination = tmp_path.parent / tmp_path.stem
                logger.debug('Replacing %s with %s', destination, source)
                source.replace(destination)
            logger.info('Save completed; removing dotfiles')
            phase_1_path.unlink()
            phase_2_path.unlink()
            return True
        elif phase_2_exists and not phase_1_exists:
            # Phase 2 was complete, but the dotfile did not get removed
            logger.info('Save already succeded; removing %s', phase_2_path)
            phase_2_path.unlink()
            return True
        elif phase_1_exists and not phase_2_exists:
            # We were in phase 1.  Roll the operation back
            logger.info('Rolling back save')
            tmpfile_glob = self.path.glob(TMP_GLOB)
            for path in tmpfile_glob:
                logger.debug('Removing %s', path)
                path.unlink()
            logger.info('Save reverted; removing %s', phase_1_path)
            phase_1_path.unlink()
            return False
        else:
            # Neither dotfile exists; the directory is "clean"
            assert not phase_1_exists and not phase_2_exists
            logger.info('Directory is clean; nothing to do')
            return True

    @property
    def max_cache(self):
        """See :attr:`Dimension.max_cache`"""
        return self._max_cache

    @max_cache.setter
    def max_cache(self, new_max_cache: int):
        new_max_cache = int(new_max_cache)
        if new_max_cache < -1:
            raise ValueError("max_cache must be at least -1")
        self._max_cache = new_max_cache
        self._flush_cache()

    def flush_cache(self, save=True):
        """See :meth:`Dimension._flush_cache`"""
        if self.max_cache == -1:
            return
        if self._atomic:
            return
        while len(self.regions) > self.max_cache:
            coords, reg = self.regions.popitem(last=False)
            if save:
                r_path = self.path / TMP_FORMAT.format(*coords)
                with r_path.open(mode='wb') as output:
                    reg.save(output)
                r_path.replace(self.path / REGION_FORMAT.format(*coords))

    @property
    def cache_size(self):
        """See :attr:Dimension.cache_size`"""
        return len(self.regions)

    def get_region(self, r_x: int, r_z: int) -> region.Region:
        """See :meth:`Dimension._getregion`."""
        try:
            result = self.regions[r_x, r_z]
        except KeyError:
            pass  # See below...
        else:
            self.regions.move_to_end((r_x, r_z))
            return result

        # It's not in self.regions, so generate it by hand
        region_path = self.path / REGION_FORMAT.format(r_x, r_z)
        try:
            region_file = region_path.open(mode='rb')
        except FileNotFoundError as err:
            if self.fill_value is not None:
                logger.info('Region %d, %d does not exist, filling in %r',
                            r_x, r_z, self.fill_value)
                r = region.Region(r_x, r_z)
                for x, z in itertools.product(range(REGION_CHUNKS), repeat=2):
                    cnk = chunk.Chunk()
                    for y in range(SECTIONS_PER_CHUNK):
                        sec = chunk.Section()
                        sec.blocks[...] = self.fill_value
                        cnk.sections[y] = sec
                    r[x, z] = cnk
            else:
                raise IndexError('Region {}, {} does not exist'
                                 .format(r_x, r_z)) from err
        else:
            with region_file:
                r = region.Region.load(r_x, r_z, region_file)
        self.regions[r_x, r_z] = r
        return r


class _EntitySliceable:
    def __init__(self, dim: Dimension):
        self.dim = dim

    @staticmethod
    def _slice_cleanup(idx: (slice, slice, slice)) -> (slice, slice, slice):
        try:
            x_slice, y_slice, z_slice = idx
        except ValueError as ve:
            raise TypeError('Only 3D slicing allowed') from ve
        if any(s.step is not None for s in (x_slice, y_slice, z_slice)):
            raise ValueError('You may not specify a step')
        if any(s.start is None or s.stop is None for s in (x_slice, z_slice)):
            raise ValueError('Unbounded slicing in the X or Z dimension')
        y_slice = slice(*y_slice.indices(HEIGHT_LIMIT))
        return x_slice, y_slice, z_slice

    @staticmethod
    def _in_range(idx: (slice, slice, slice)) -> callable:
        return lambda ent: all(sl.start <= coord < sl.stop
                               for sl, coord in zip(idx, ent.pos))

    @_cache_correct
    def __getitem__(self, idx: (slice, slice, slice)) -> {entity.Entity}:
        x_slice, y_slice, z_slice = self._slice_cleanup(idx)
        idx = (x_slice, y_slice, z_slice)
        in_range = self._in_range(idx)
        x_range, _, z_range = self.dim._make_chunk_range(*idx)
        result = set()
        for c_x, c_z in itertools.product(x_range, z_range):
            ck = self.dim._getchunk(c_x, c_z)
            result.update(x for x in ck.entities if in_range(x))
        return result

    @_cache_correct
    def __setitem__(self, idx: (slice, slice, slice), seq: {entity.Entity}):
        x_slice, y_slice, z_slice = self._slice_cleanup(idx)
        idx = (x_slice, y_slice, z_slice)
        mapping = collections.defaultdict(set)

        seq = set(seq)

        # First, figure out which chunk each entity belongs to
        for ent in seq:
            x, y, z = ent.pos
            mapping[int(x)//CHUNK_BLOCKS, int(z)//CHUNK_BLOCKS].add(ent)

        in_range = self._in_range(idx)

        # Now, for each chunk...
        x_range, _, z_range = self.dim._make_chunk_range(x_slice,
                                                         y_slice,
                                                         z_slice)
        for c_x, c_z in itertools.product(x_range, z_range):
            ck = self.dim._getchunk(c_x, c_z)
            # Attach all the entities belonging to that chunk, plus
            # already-present entities which were not in the range specified.
            # Start with the custom entities so they take precedence over
            # duplicates.
            # XXX: Not sure if this behavior of set.union() is contractual.
            ck.entities[:] = mapping[c_x, c_z].union(ent
                                                     for ent in ck.entities
                                                     if not in_range(ent))

    def __delitem__(self, idx):
        self.__setitem__(self, idx, set())

    def _flush_cache(self):
        return self.dim._flush_cache()


class _AtomicContext(contextlib.ContextDecorator):
    def __init__(self, owner: _RegionManager):
        self.owner = owner
        self.stack = []

    def __enter__(self):
        if self.owner._atomic:
            self.stack.append(False)
        else:
            self.owner.save_all()
            self.owner._atomic = True
            self.stack.append(True)

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.stack.pop():
            return False
        if exc_type is None:
            self.owner.save_all()
        else:
            # Throw out the cache entirely
            self.owner.regions = collections.OrderedDict()
        self.owner._atomic = False
        self.owner.flush_cache(save=False)
        # Do not suppress exceptions
        return False
