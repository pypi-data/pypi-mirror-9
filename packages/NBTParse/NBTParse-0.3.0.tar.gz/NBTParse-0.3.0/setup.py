#!/usr/bin/env python

import os
import os.path
import sys

from setuptools import setup, Extension

with open(os.path.join('nbtparse', '__version__.txt'), mode='rb') as fileobj:
    version = fileobj.read().decode('utf8', errors='ignore').strip()

ON_RTD = os.environ.get('READTHEDOCS', None) == 'True'

USE_CYTHON = '--cythonize' in sys.argv
EXT = '.pyx' if USE_CYTHON else '.c'

if '--pure-python' in sys.argv:
    sys.argv.remove('--pure-python')
    ext_modules = []
elif ON_RTD:
    ext_modules = []
else:
    ext_modules = [Extension('nbtparse.minecraft.terrain._cVoxel',
                             ['nbtparse/minecraft/terrain/_cVoxel'+EXT])]

if USE_CYTHON:
    sys.argv.remove('--cythonize')
    from Cython.Build import cythonize # Only import if asked
    ext_modules = cythonize(ext_modules)

setup(name='NBTParse',
      version=version,
      author='Kevin Norris',
      author_email='nykevin.norris@gmail.com',
      url='https://bitbucket.org/NYKevin/nbtparse',
      packages=['nbtparse', 'nbtparse.syntax', 'nbtparse.semantics',
      'nbtparse.minecraft', 'nbtparse.minecraft.terrain'],
      package_data={'nbtparse': ['__version__.txt',
                                 'minecraft/standard.json']},
      entry_points={'console_scripts':
                    ['minecraft_id = nbtparse.minecraft.ids:main']},
      ext_modules=ext_modules,
      classifiers=[
                   'Development Status :: 2 - Pre-Alpha',
                   'License :: OSI Approved :: BSD License',
                   'Topic :: Games/Entertainment',
                   'Topic :: Software Development :: Libraries',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3',
                   ],
      license='BSD (3-clause)',
      description="NBT swiss army knife",
      long_description=
      """NBTParse is a Python "swiss army knife" for Named Binary Tags.

      NBT is the data format used by Minecraft.

      It follows the `unofficial specification`__ on the Minecraft Wiki.

      __ http://www.minecraftwiki.net/wiki/NBT_format

      Support for the more complex elements of Minecraft is under ongoing
      development.

      """,
      zip_safe=False,
)
