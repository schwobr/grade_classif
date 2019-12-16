#AUTOGENERATED! DO NOT EDIT! File to edit: dev/00_core.ipynb (unless otherwise specified).

__all__ = ['ifnone', 'is_listy']

#Cell
import numpy as np

#Cell
def ifnone(a, b):
    "`b` if `a` is None else `a`"
    return b if a is None else a

#Cell
def is_listy(x):
    return isinstance(x, (tuple,list))