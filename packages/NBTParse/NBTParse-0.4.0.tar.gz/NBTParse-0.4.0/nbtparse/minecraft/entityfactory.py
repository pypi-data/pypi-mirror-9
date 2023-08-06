"""Module for producing :class:`.entity.Entity` instances."""

import logging

from ..syntax import tags
from ..semantics import nbtobject
from . import entity
from . import entity_ids


logger = logging.getLogger(__name__)


def from_nbt(nbt: tags.CompoundTag, *, default_class:
             nbtobject.NBTMeta=entity.Entity,
             namespace: str='minecraft') -> nbtobject.NBTObject:
    """Factory function for making entities and tile entities from raw NBT.

    Uses appropriate subclasses (usually of :class:`~.entity.Entity` and
    :class:`~.tile.TileEntity`) where necessary.  The choice of subclass is
    made via the :mod:`~.minecraft.entity_ids` module, and may be altered by
    registering classes and modules with it.

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
        subclass = entity_ids.EntityNamespace(namespace)[name]
    except KeyError:
        logger.warning("Entity ID %r unrecognized in namespace %r",
                       name, namespace, exc_info=True)
        return fallback()
    return subclass.from_nbt(nbt)
