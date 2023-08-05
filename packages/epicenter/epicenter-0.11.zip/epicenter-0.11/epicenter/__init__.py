"""
Imports here are performed so that "from epicenter import Epicenter" works as
an import in models.
"""
from __future__ import absolute_import

from .epicenter import Epicenter
from .interface import VariableSetter

# Version number is tracked on PyPi
__version__ = 0.11
