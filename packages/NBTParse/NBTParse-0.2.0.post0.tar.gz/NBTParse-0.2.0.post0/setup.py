#!/usr/bin/env python

import os.path
import sys

from setuptools import setup, Extension

if '--cython' in sys.argv:
    sys.argv.remove('--cython')
    from Cython.Build import cythonize # Only import if asked
    ext_modules = cythonize([Extension('nbtparse.minecraft.terrain._cVoxel',
                                       ['nbtparse/minecraft/terrain/'
                                        '_cVoxel.pyx']),
                            ])
else:
    ext_modules = []


with open(os.path.join('nbtparse', '__version__.txt'), mode='rb') as fileobj:
    version = fileobj.read().decode('utf8', errors='ignore').strip()


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
