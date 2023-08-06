"""Minecraft-related NBTParse modules.

The modules in this package all relate to high-level files and data
structures.  For instance, :mod:`nbtparse.minecraft.level` contains the
:class:`~.level.LevelFile` class, which can read and write the ``level.dat``
file in a standard Minecraft save.

"""

from . import entity_ids, item, mobs, projectile
from .terrain import tile


for module in (item, mobs, projectile, tile):
    entity_ids.EntityNamespace('minecraft').register_module(module)
