#AUTOGENERATED! DO NOT EDIT! File to edit: dev/_train_classif.ipynb (unless otherwise specified).

__all__ = []

#Cell
from .params.parser import hparams
from .train import train_classifier
from .imports import *

#Cell
torch.cuda.set_device(hparams.gpus[0])

#Cell
train_classifier(hparams)