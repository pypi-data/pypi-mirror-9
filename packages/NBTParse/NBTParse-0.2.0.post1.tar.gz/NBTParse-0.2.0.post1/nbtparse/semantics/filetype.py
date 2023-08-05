"""Provides classes for working with NBT files as objects.

These classes extend :mod:`nbtparse.semantics.nbtobject` and provide save
and load methods so the file can be easily (de)serialized.

"""

import gzip
import io

from ..syntax import tags
from . import nbtobject


class NBTFile(nbtobject.NBTObject):
    """Simple class for handling NBT encoded files holistically.

    An entire NBT file is read and decoded via
    :func:`tags.decode_named<nbtparse.syntax.tags.TagMixin.decode_named>`, and
    then converted into a Pythonic object.

    """
    def save(self, output: io.BufferedIOBase, rootname: str=''):
        """Writes this file to output as NBT.

        The root tag will be called :obj:`rootname`.

        """
        nbt = self.to_nbt()
        nbt.encode_named(rootname, output)

    @classmethod
    def load(cls, input: io.BufferedIOBase):
        """Creates a new :class:`NBTFile` from the input file-like.

        Returns :obj:`(rootname, NBTFile)`, where :obj:`rootname` is the name
        of the root tag.  Conventional :class:`.NBTObject`\ s do not make use
        of their external names, so if you intend to use it somewhere, you
        need to capture it here.

        """
        rootname, nbt = tags.decode_named(input)
        return (rootname, cls.from_nbt(nbt))


class GzippedNBTFile(NBTFile):
    """`Gzipped`_ variant of :class:`NBTFile`.

    .. _Gzipped: http://en.wikipedia.org/wiki/gzip

    """
    def save(self, output: io.BufferedIOBase, rootname: str=''):
        """Writes this file to output as gzipped NBT."""
        with gzip.GzipFile(mode='wb', fileobj=output) as gzipped_file:
            super().save(gzipped_file, rootname)

    @classmethod
    def load(cls, input: io.BufferedIOBase):
        """Creates a new :class:`NBTFile` from the gzipped input file-like."""
        with gzip.GzipFile(mode='rb', fileobj=input) as gzipped_file:
            return super().load(gzipped_file)
