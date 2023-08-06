"""Named Binary Tag manipulation tools.

This package contains various utilities for manipulating NBT-formatted data.

NBT is used by Minecraft to store a variety of data and metadata.

* :mod:`.syntax` contains modules relating to low-level NBT syntax.
* :mod:`.semantics` contains modules relating to intermediate-level
  constructs.
* :mod:`.minecraft` contains modules directly relating to Minecraft's file and
  data structures.

NBTParse logs to loggers with the same names as its modules and packages.  You
can therefore control logging for the entire package via the NBTParse root
logger::

    nbtparse_root_logger = logging.getLogger('nbtparse')

By default (as of Python 3.4), the logging package will emit warnings and more
severe logged events on :obj:`sys.stderr`, while dropping less severe events.
Consult the `logging documentation`_ if you wish to override this behavior.

.. _logging documentation: https://docs.python.org/3/library/logging.html

"""

# Python version check; this must happen before everything else
import sys


if sys.hexversion < 0x03040000:
    raise ImportError('NBTParse requires Python 3.4 or later.')


import pkgutil


_version_string = pkgutil.get_data(__name__, '__version__.txt')
if _version_string is not None:
    _version_string = _version_string.decode('utf8', errors='ignore').strip()


#: The version number string for NBTParse, or None if version information is
#: not available.  The numbering scheme is strictly compatible with
#: `PEP 440`_ and loosely compatible with `Semantic Versioning`_, allowing
#: some deviations from the latter to satisfy the former.
#:
#: .. _PEP 440: http://legacy.python.org/dev/peps/pep-0440/
#: .. _Semantic Versioning: http://semver.org
#:
#: Strictly speaking, NBTParse does not comply with SemVer at all, and the
#: above link is at best misleading.  This results from SemVer's heavy use of
#: the MUST keyword.
#:
#: .. note::
#:
#:     As a matter of policy, this value ends in ``.dev0`` on the trunk.
#:     Since the version number is not changed from one commit to the next,
#:     trunk snapshots may appear to have the same version number even if they
#:     are materially different.  Such snapshots are not official releases.
__version__ = _version_string

del _version_string
