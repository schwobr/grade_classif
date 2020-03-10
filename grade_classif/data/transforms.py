#AUTOGENERATED! DO NOT EDIT! File to edit: dev/14_data.transforms.ipynb (unless otherwise specified).

__all__ = ['DeterministicHSV', 'DeterministicBrightnessContrast', 'DeterministicGamma', 'get_transforms1',
           'get_transforms2', 'get_transforms3', 'get_transforms4']

#Cell
from albumentations import (RandomRotate90,
                            Flip,
                            Transpose,
                            GridDistortion,
                            RandomCrop,
                            GaussianBlur,
                            RandomGamma,
                            RandomBrightnessContrast,
                            HueSaturationValue,
                            RGBShift,
                            CenterCrop)
from ..imports import *

#Cell
def _get_params(tfm):
    params = {}
    for k, v in tfm.base_values.items():
        v_min, v_max = tfm.max_values[k]
        p = v + tfm.n * tfm.mult
        p = (p - v_min) % (v_max - v_min) + v_min
        params[k] = p
    tfm.n += 1
    tfm.n %= tfm.num_els
    return params

#Cell
class DeterministicHSV(HueSaturationValue):
    def __init__(self, num_els=1, **kwargs):
        super().__init__(**kwargs)
        _init_attrs(self, HueSaturationValue, num_els)
        self.max_values = {"hue_shift": self.hue_shift_limit,
                           "sat_shift": self.sat_shift_limit,
                           "val_shift": self.val_shift_limit}

    def get_params(self):
        return _get_params(self)

#Cell
class DeterministicBrightnessContrast(RandomBrightnessContrast):
    def __init__(self, num_els=1, **kwargs):
        super().__init__(**kwargs)
        _init_attrs(self, RandomBrightnessContrast, num_els)
        self.max_values = {"alpha": tuple(x + 1 for x in self.contrast_limit),
                           "beta": self.brightness_limit}

    def get_params(self):
        return _get_params(self)

#Cell
class DeterministicGamma(RandomGamma):
    def __init__(self, num_els=1, **kwargs):
        super().__init__(**kwargs)
        _init_attrs(self, RandomGamma, num_els)
        self.max_values = {"gamma": tuple(x/100 for x in self.gamma_limit)}

    def get_params(self):
        return _get_params(self)

#Cell
def get_transforms1(size, num_els=1):
    tfms = [RandomRotate90(),
            Flip(),
            Transpose(),
            GridDistortion(distort_limit=0.05, p=0.2),
            RandomGamma(p=0.2),
            GaussianBlur(blur_limit=3, p=0.2),
            RandomCrop(size, size)]
    val_tfms = [CenterCrop(size, size)]
    return tfms, val_tfms

#Cell
def get_transforms2(size, num_els=1):
    tfms = [RandomRotate90(),
            Flip(),
            Transpose(),
            GridDistortion(distort_limit=0.05, p=0.2),
            RandomGamma(p=0.2),
            GaussianBlur(blur_limit=3, p=0.2),
            RGBShift(0.15, 0.15, 0.15),
            RandomCrop(size, size)]
    val_tfms = [CenterCrop(size, size)]
    return tfms, val_tfms

#Cell
def get_transforms3(size, num_els=1):
    tfms = [RandomRotate90(),
            Flip(),
            Transpose(),
            GridDistortion(distort_limit=0.05, p=0.2),
            RandomBrightnessContrast(p=0.7),
            GaussianBlur(blur_limit=3, p=0.2),
            RGBShift(0.2, 0.2, 0.2, p=0.8),
            RandomCrop(size, size)]
    val_tfms = [RandomBrightnessContrast(p=0.7),
                RGBShift(0.2, 0.2, 0.2, p=0.7),
                CenterCrop(size, size)]
    return tfms, val_tfms

#Cell
def get_transforms4(size, num_els=1):
    tfms = [RandomRotate90(),
            Flip(),
            Transpose(),
            GridDistortion(distort_limit=0.05, p=0.2),
            RandomBrightnessContrast(0.2, 0., p=0.2),
            GaussianBlur(blur_limit=3, p=0.2),
            RandomGamma(gamma_limit=(40, 160), p=0.8),
            HueSaturationValue(30, 0., 0, p=0.8),
            RandomCrop(size, size)]
    val_tfms = [DeterministicGamma(num_els=num_els, gamma_limit=(40, 160)),
                DeterministicBrightnessContrast(num_els=num_els, brightness_limit=0.2, contrast_limit=0.),
                DeterministicHSV(num_els=num_els, hue_shift_limit=30, sat_shift_limit=0., val_shift_limit=0.),
                CenterCrop(size, size)]
    return tfms, val_tfms