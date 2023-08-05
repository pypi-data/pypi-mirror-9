"""Module for producing :class:`.entity.Entity` instances."""

import logging

from ..syntax import tags
from ..semantics import nbtobject
from . import entity
from . import ids


logger = logging.getLogger(__name__)


def from_nbt(nbt: tags.CompoundTag, *, default_class:
             nbtobject.NBTMeta=entity.Entity) -> nbtobject.NBTObject:
    """Factory function for making entities and tile entities from raw NBT.

    Uses appropriate subclasses (usually of :class:`~.entity.Entity` and
    :class:`~.tile.TileEntity`) where necessary.  The choice of subclass is
    made via the :mod:`~.minecraft.ids` module, and may be altered by
    registering a custom namespace or re-registering a custom version of the
    standard namespace.

    Tries to defend against invalid input.  If there is no ID or the ID is
    unrecognized, a warning will be logged on the module's logger, and a plain
    instance of `default_class` is returned instead.

    """
    fallback = lambda: default_class.from_nbt(nbt)
    try:
        name = nbt['id']
    except KeyError:
        logger.warning("Entity ID not found in given NBT", exc_info=True)
        return fallback()
    try:
        name = str(name)
    except TypeError:
        logger.warning('Entity ID of wrong type', exc_info=True)
        return fallback()
    try:
        ident = ids.all_ids[name]
    except KeyError:
        logger.warning("Entity ID %r unrecognized", name, exc_info=True)
        return fallback()
    else:
        subclass = ident.resolve_class()
        return subclass.from_nbt(nbt)
