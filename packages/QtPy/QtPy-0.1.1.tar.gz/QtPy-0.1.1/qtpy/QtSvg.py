# -*- coding: utf-8 -*-
#
# Copyright © 2012 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Provides QtSvg classes and functions.
"""

import os
from qtpy import QT_API
from qtpy import PYQT5_API
from qtpy import PYQT4_API
from qtpy import PYSIDE_API
from qtpy import PythonQtError


if os.environ[QT_API] in PYQT5_API:
    from PyQt5.QtSvg import *                                 # analysis:ignore
elif os.environ[QT_API] in PYQT4_API:
    from PyQt4.QtSvg import *                                 # analysis:ignore
elif os.environ[QT_API] in PYSIDE_API:
    from PySide.QtSvg import *                                # analysis:ignore
else:
    raise PythonQtError('No Qt bindings could be found')


