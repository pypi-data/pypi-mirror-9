"""Terrain-related NBTParse modules.

This package consists of modules relating to Minecraft terrain.  The basic
unit of terrain manipulation is :class:`.voxel.VoxelBuffer`, which is used to
store blocks of terrain and tile entity data compactly.

"""

import logging
import sys

logger = logging.getLogger(__name__)

try:
    from . import _cVoxel as voxel
except ImportError:
    logger.info('Cython version of voxel not available, falling back to '
                'pure Python version.', exc_info=True)
    from . import _voxel as voxel


name = __name__.split('.')
name.append('voxel')
name = '.'.join(name)
sys.modules[name] = voxel
del name
