import comet_ml
import os
import sys
import cv2
import timm
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import random
from dataclasses import dataclass
from functools import partial
from io import StringIO 
from typing import Dict, Iterable, List, Optional, Union, Callable, Any, Sequence, Tuple
from argparse import Namespace
from numbers import Number
from nptyping import NDArray
from matplotlib.axes import Axes
import warnings

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)

warnings.formatwarning = warning_on_one_line

def in_colab():
    "Check if the code is running in Google Colaboratory"
    try:
        from google import colab
        return True
    except: return False
    
def in_notebook():
    "Check if the code is running in a jupyter notebook"
    if in_colab(): return True
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell': # Jupyter notebook, Spyder or qtconsole
            import IPython
            #IPython version lower then 6.0.0 don't work with output you update
            return IPython.__version__ >= '6.0.0'
        elif shell == 'TerminalInteractiveShell': return False  # Terminal running IPython
        else: return False  # Other type (?)
    except NameError: return False      # Probably standard Python interpreter

IN_NOTEBOOK = in_notebook()

if IN_NOTEBOOK:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm

np.set_printoptions(threshold=10)

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout
        
def imread(fn, *args, **kwargs):
    img = cv2.imread(str(fn), *args, **kwargs)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img
