#AUTOGENERATED! DO NOT EDIT! File to edit: dev/03_train.ipynb (unless otherwise specified).

__all__ = ['train_normalizer', 'train_classifier']

#Cell
from .params import hparams
from .models.pl_modules import Normalizer, GradesClassifModel

#Cell
def train_normalizer(hparams):
    model = Normalizer(hparams)
    model.fit()
    return model

#Cell
def train_classifier(hparams):
    model = GradesClassifModel(hparams)
    model.fit()
    return model