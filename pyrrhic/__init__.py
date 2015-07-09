"""
PyRRHIC: Python Rtl Refactoring and High-level Ic Construction language.
"""
__all__ = ['builder', 'pyrast']

from pyrast import *
import builder
from builder.bdast import *
import math

def Log2Up(e):
    return int(math.ceil(math.log(e)/ math.log(2.)))
