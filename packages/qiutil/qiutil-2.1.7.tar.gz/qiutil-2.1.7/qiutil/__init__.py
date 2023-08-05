"""The Quantitative Imaging utility module."""

__version__ = '2.1.7'
"""
The one-based major.minor.patch version.
The version numbering scheme loosely follows http://semver.org/.
The major version is incremented when a significant feature
set is introduced. The minor version is incremented when there
is a functionality change. The patch version is incremented when
there is a refactoring or bug fix. All major, minor and patch
version numbers begin at 1.
"""

# Import collections, file and logging, since these are also
# standard Python libraries. This import allows the client to
# use the nested modules directly, e.g.:
#   with qiutil.file.open(...):
# rather than:
#   from qiutil import file
#   with file.open(...): # Misleading
#  or:
#   from qiutil import file as qifile
#   with qifile.open(...): # Awkward
from . import (collections, file, logging) 
