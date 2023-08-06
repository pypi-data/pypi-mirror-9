"""Package for Comparable."""

import sys

__project__ = 'Comparable'
__version__ = '1.0'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 3

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    from comparable.base import SimpleComparable, CompoundComparable
    from comparable import simple
    from comparable import compound
    from comparable import tools
except ImportError:  # pragma: no cover (manual test)
    pass
