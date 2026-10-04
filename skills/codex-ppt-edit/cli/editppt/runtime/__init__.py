"""Deterministic runtime modules behind the public editppt CLI.

The runtime modules import each other by flat module name because they are
also executed directly as scripts. Register this directory on sys.path so the
same flat imports resolve when the modules are imported as
``editppt.runtime.<module>`` from the installed package.
"""

import sys as _sys
from pathlib import Path as _Path

_RUNTIME_DIR = str(_Path(__file__).resolve().parent)
if _RUNTIME_DIR not in _sys.path:
    _sys.path.insert(0, _RUNTIME_DIR)
