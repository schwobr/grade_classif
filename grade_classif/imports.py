import os
import sys
import cv2
import timm
from tqdm import tqdm
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
        
def imread(*args, **kwargs):
    img = cv2.imread(*args, **kwargs)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img
