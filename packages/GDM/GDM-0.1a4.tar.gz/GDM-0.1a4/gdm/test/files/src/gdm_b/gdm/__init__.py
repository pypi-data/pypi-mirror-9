"""Package for GDM."""

import sys

__project__ = 'GDM'
__version__ = '0.0.0'

CLI = 'gdm'
VERSION = __project__ + '-' + __version__
DESCRIPTION = "A very basic language-agnostic dependency manager using Git."

PYTHON_VERSION = 3, 4

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    from .commands import install
except ImportError:
    pass
