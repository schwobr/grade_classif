import os
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

np.set_printoptions(threshold=10)