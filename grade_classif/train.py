#AUTOGENERATED! DO NOT EDIT! File to edit: dev/01_train.ipynb (unless otherwise specified).

__all__ = ['train_normalizer', 'train_classifier']

#Cell
from .models.plmodules import Normalizer, GradesClassifModel
from .models.metrics import accuracy, precision, recall, f_1
from .imports import *

#Cell
def train_normalizer(hparams):
    model = Normalizer(hparams)
    model.freeze_encoder()
    model.fit(amp_level='O1', use_amp=True)
    return model

#Cell
def train_classifier(hparams):
    model = GradesClassifModel(hparams, metrics=[accuracy] + [met for i in range(2) for met in (partial(precision, cat=i), partial(recall, cat=i), partial(f_1, cat=i))])
    model.fit()
    return model