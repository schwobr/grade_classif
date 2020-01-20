#AUTOGENERATED! DO NOT EDIT! File to edit: dev/80_params.defaults.ipynb (unless otherwise specified).

__all__ = ['PROJECT', 'CSVS', 'LEVEL', 'FULL_DATA', 'DATA', 'DATA_CSV', 'MODELS', 'NORM_CSV', 'CONCEPTS',
           'CONCEPT_CLASSES', 'MODEL', 'GPUS', 'SIZE', 'BATCH_SIZE', 'LOSS', 'SCHED', 'REDUCTION', 'EPOCHS', 'DROPOUT',
           'LR', 'WD', 'WEIGHT', 'NORMALIZER', 'NORM_VERSION', 'NORM_VERSIONS', 'PRED_LEVELS', 'VERSIONS', 'SCAN',
           'FILT']

#Cell
from ..imports import *

#Cell
PROJECT = Path('/home/DeepLearning/grade_classif')
_PROJECT = Path('/work/stages/schwob/grade_classif')
CSVS = PROJECT/'csvs'
LEVEL = 1
FULL_DATA = Path(f'/data/DeepLearning/SCHWOB_Robin/new_patches')
_FULL_DATA = Path(f'/work/stages/schwob/Patches_256')
DATA = FULL_DATA/f'Patches_256_{LEVEL}'
DATA_CSV = CSVS/f'scans.csv'
MODELS = Path('/data/DeepLearning/SCHWOB_Robin/models/logs')
_MODELS = PROJECT/'models/logs'
NORM_CSV = CSVS/'categories.csv'
CONCEPTS = DATA/f'concepts_{LEVEL}.csv'
_CONCEPTS = None
CONCEPT_CLASSES = CSVS/'concept_classes.csv'
_CONCEPT_CLASSES = None
MODEL = 'cbr_5_64_4'
GPUS = [0]
SIZE = 224
BATCH_SIZE = 64
LOSS = 'cross-entropy'
SCHED = 'one-cycle'
REDUCTION = 'mean'
EPOCHS = 50
DROPOUT= 0.5
LR = 1e-3
WD = 0.1
WEIGHT = 2.
NORMALIZER = None
NORM_VERSION = 11
NORM_VERSIONS = [0]
PRED_LEVELS = [1]
VERSIONS = ['10']
SCAN = None
FILT = 'K'