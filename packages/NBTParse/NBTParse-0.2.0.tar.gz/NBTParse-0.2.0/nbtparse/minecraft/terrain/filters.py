import collections
import collections.abc as cabc
import functools
import itertools

from . import voxel


def _require_open(wrapped: callable) -> callable:
    @functools.wraps(wrapped)
    def wrapper(self, *args, **kwargs):
        if self._vb is None:
            raise RuntimeError('Filter is closed')
        return wrapped(*args, **kwargs)
    return wrapper


class Filter(cabc.Mapping):
    """Filter for rapidly finding all blocks of a given type.

    Keys are Block objects or integers.  Values are sets of (x, y, z)
    3-tuples.  Filters maintain the following invariants::

        vb = VoxelBuffer(...)  # with arbitrary contents
        block = Block(number, data)
        filter = Filter(vb)
        ((x, y, z) in filter[block]) == (vb[x, y, z] == block)
        ((x, y, z) in filter[number]) == (vb[x, y, z].id == number)

    The filter updates automatically when the VoxelBuffer changes.

    Initially constructing a filter is expensive, but keeping it up-to-date is
    relatively cheap.  You may realize performance gains by constructing a
    single filter and reusing it many times.

    Integer keys will not appear in iteration, because the same information is
    already available via block keys.

    """
    def __init__(self, vb: voxel.VoxelBuffer):
        self._vb = vb

        # from Block() to (x, y, z)
        self._by_block = collections.defaultdict(set)

        # from Block().id to (x, y, z)
        self._by_int = collections.defaultdict(set)

        self._previous = vb  # The notify call below will make a copy

        vb.watch(self._notify)
        self._notify(range(vb.length), range(vb.height), range(vb.width)) 

    def __repr__(self):
        return '<Filter attached to {!r}>'.format(self._vb)

    def _notify_block(self, x: int, y: int, z: int):
        old_block = self._previous[x, y, z]
        new_block = self._vb[x, y, z]
        # Do the discard first so it doesn't undo the add
        # (if old_block == new_block)
        self._by_block[old_block].discard((x, y, z))
        self._by_int[old_block.id].discard((x, y, z))
        self._by_block[new_block].add((x, y, z))
        self._by_int[new_block.id].add((x, y, z))

    @_require_open
    def _notify(self, x_arg, y_arg, z_arg):
        if type(x_arg) is int:
            self._notify_block(x_arg, y_arg, z_arg)
        else:
            for x, y, z in itertools.product(x_arg, y_arg, z_arg):
                self._notify_block(x, y, z)
        self._previous = self._vb[...]

    @_require_open
    def __getitem__(self, key):
        if type(key) is int:
            return set(self._by_int[key])
        elif type(key) is voxel.Block:
            return set(self._by_block[key])
        else:
            raise KeyError(key)

    @_require_open
    def __iter__(self):
        return iter(self._by_block)

    @_require_open
    def __len__(self):
        return len(self._by_block)

    def close(self):
        """Close this filter so it can no longer be used.

        Filters slow down the VoxelBuffers they are attached to.  Closing them
        is good practice.  Using a filter as a context manager will close it
        automatically when the context is exited::

            with Filter(vb) as filt:
                pass

        Closing a filter twice is legal and has no effect.  Doing anything
        else with a closed filter will raise a :exc:`RuntimeError`.

        """
        if self._vb is None:
            return

        self._vb.unwatch(self._notify)
        self._vb = None
        
        # Try to minimize memory consumption; shut down everything else
        self._previous = None
        self._by_block = None
        self._by_int = None

    @_require_open
    def copy_vb(self) -> voxel.VoxelBuffer:
        """Return a copy of the VoxelBuffer and attach to it.

        This will detach the filter from the original VoxelBuffer, so it will
        track the copy instead.

        This is equivalent to the following code, but significantly faster::

            filter.close()
            copy = vb[...]
            filter = Filter(copy)

        """
        self._vb.unwatch(self._notify)
        self._vb = self._previous
        self._previous = self._vb[...]
        self._vb.watch(self._notify)
        return self._vb

    @_require_open
    def __enter__(self):
        return self

    def __exit__(self, exc1, exc2, exc3):
        self.close()
        return False  # Do not suppress exceptions
