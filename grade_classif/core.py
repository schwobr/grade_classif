#AUTOGENERATED! DO NOT EDIT! File to edit: dev/00_core.ipynb (unless otherwise specified).

__all__ = ['ifnone']

#Cell
from test_tube import HyperOptArgumentParser
from .defaults import *
from pathlib import Path

#Cell
def ifnone(a, b):
    "`b` if `a` is None else `a`"
    return b if a is None else a