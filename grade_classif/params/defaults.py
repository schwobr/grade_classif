#AUTOGENERATED! DO NOT EDIT! File to edit: dev/80_params_defaults.ipynb (unless otherwise specified).

__all__ = ['PROJECT', 'LEVEL', 'FULL_DATA', 'DATA', 'DATA_CSV', 'MODELS', 'NORM_CSV', 'MODEL', 'GPUS', 'SIZE',
           'BATCH_SIZE', 'LOSS', 'SCHED', 'REDUCTION', 'EPOCHS', 'DROPOUT', 'LR', 'WD', 'WEIGHT', 'NORMALIZER',
           'NORM_VERSION', 'NORM_VERSIONS', 'PRED_LEVELS', 'VERSIONS', 'SCAN']

#Cell
from pathlib import Path

#Cell
PROJECT = Path('/home/DeepLearning/grades_classif')
_PROJECT = Path('/work/stages/schwob/grades_classif')
LEVEL = 3
FULL_DATA = Path(f'/data/DeepLearning/SCHWOB_Robin/Patches_256')
_FULL_DATA = Path(f'/work/stages/schwob/Patches_256')
DATA = FULL_DATA/f'Patches_MGI_256_{LEVEL}'
DATA_CSV = FULL_DATA/f'scans.csv'
MODELS = Path('/data/DeepLearning/SCHWOB_Robin/models/logs')
_MODELS = PROJECT/'models/logs'
NORM_CSV = PROJECT/'categories.csv'
MODEL = 'resnet34'
GPUS = [0]
SIZE = 224
BATCH_SIZE = 16
LOSS = 'cross-entropy'
SCHED = 'one-cycle'
REDUCTION = 'mean'
EPOCHS = 50
DROPOUT= 0.5
LR = 1e-3
WD = 0.01
WEIGHT = 1.
NORMALIZER = None
NORM_VERSION = 11
NORM_VERSIONS = [0, 0, 0, 0]
PRED_LEVELS = [1, 3, 5, 7]
VERSIONS = [0, 0, 0, 0]
SCAN = None