#AUTOGENERATED! DO NOT EDIT! File to edit: dev/14_data.transforms.ipynb (unless otherwise specified).

__all__ = ['get_transforms1', 'get_transforms2', 'get_transforms3']

#Cell
from albumentations import (RandomRotate90,
                            Flip,
                            Transpose,
                            GridDistortion,
                            RandomCrop,
                            GaussianBlur,
                            RandomGamma,
                            RGBShift)

#Cell
def get_transforms1(size):
    tfms = [RandomRotate90(),
            Flip(),
            Transpose(),
            GridDistortion(distort_limit=0.05, p=0.2),
            RandomGamma(p=0.2),
            GaussianBlur(blur_limit=3, p=0.2),
            RandomCrop(size, size)]
    val_tfms = [RandomCrop(size, size)]
    return tfms, val_tfms

#Cell
def get_transforms2(size):
    tfms = [RandomRotate90(),
            Flip(),
            Transpose(),
            GridDistortion(distort_limit=0.05, p=0.2),
            RandomGamma(p=0.2),
            GaussianBlur(blur_limit=3, p=0.2),
            RGBShift(0.15, 0.15, 0.15),
            RandomCrop(size, size)]
    val_tfms = [RandomCrop(size, size)]
    return tfms, val_tfms

#Cell
def get_transforms3(size):
    tfms = [RandomRotate90(),
            Flip(),
            Transpose(),
            GridDistortion(distort_limit=0.05, p=0.2),
            RandomGamma(p=0.5),
            GaussianBlur(blur_limit=3, p=0.2),
            RGBShift(0.15, 0.15, 0.15, p=0.7),
            RandomCrop(size, size)]
    val_tfms = [RandomCrop(size, size)]
    return tfms, val_tfms