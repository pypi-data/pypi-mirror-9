from .patches import apply_patches
apply_patches()

from .module_globals import _context_stack

from builder import ParameterSetBuilder

import sys

# DO NOT TOUCH THE FOLLOWING LINE:
if not getattr(sys, "frozen", False):
    import pkg_resources  # part of setuptools
    __version__ = tuple(map(int, pkg_resources.require(__name__)[0].version.split(".")))
else:
    __version__ = (0, 0, 0)
