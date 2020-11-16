# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_core.ipynb (unless otherwise specified).

__all__ = ['ifnone', 'is_listy']

# Cell
from .imports import *

# Cell
def ifnone(a: Any, b: Any) -> Any:
    "`b` if `a` is None else `a`"
    return b if a is None else a

# Cell
def is_listy(x: Any) -> bool:
    return isinstance(x, (tuple,list))