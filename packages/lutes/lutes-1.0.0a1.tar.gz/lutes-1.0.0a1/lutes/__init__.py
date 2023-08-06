# -*- coding: utf-8 -*-
"""
Lutes is a micro entity-component-system module.

It defines base classes to work with: Manager and System.
As entities should not contain any data, they are just mere identifiers.
"""
from .errors import LutesError, InvalidEntityError
from .component import Component
from .system import System
from .manager import Manager

__version__ = '1.0.0a1'

__all__ = ['LutesError', 'InvalidEntityError',
           'Component', 'Manager', 'System']
