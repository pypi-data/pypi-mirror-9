"""Utilities relating to low-level NBT syntax.

The package currently consists of a single module, plus a class that used to
be a module:

* :mod:`~nbtparse.syntax.tags` provides object-oriented NBT encoding
  and decoding.

* :class:`~nbtparse.syntax.ids` provides tag ID's (e.g.
  :obj:`ids.TAG_Byte<nbtparse.syntax.ids.TAG_Byte>` is 1).

"""

import enum


@enum.unique
class ids(enum.IntEnum):
    """Defines various tag ID's.

    Formerly a module, now implemented as a class.  This provides various
    benefits while retaining compatibility and a straightforward interface.

    """
    TAG_End = 0  #: ID of a TAG_End
    TAG_Byte = 1  #: ID of a TAG_Byte
    TAG_Short = 2  #: ID of a TAG_Short
    TAG_Int = 3  #: ID of a TAG_Int
    TAG_Long = 4  #: ID of a TAG_Long
    TAG_Float = 5  #: ID of a TAG_Float
    TAG_Double = 6  #: ID of a TAG_Double
    TAG_Byte_Array = 7  #: ID of a TAG_Byte_Array
    TAG_String = 8  #: ID of a TAG_String
    TAG_List = 9  #: ID of a TAG_List
    TAG_Compound = 10  #: ID of a TAG_Compound
    TAG_Int_Array = 11  #: ID of a TAG_Int_Array
