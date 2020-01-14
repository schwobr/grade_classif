#AUTOGENERATED! DO NOT EDIT! File to edit: dev/80_params.defaults.ipynb (unless otherwise specified).

__all__ = ['PROJECT', 'CSVS', 'LEVEL', 'FULL_DATA', 'DATA', 'DATA_CSV', 'MODELS', 'NORM_CSV', 'CONCEPTS',
           'CONCEPT_CLASSES', 'MODEL', 'GPUS', 'SIZE', 'BATCH_SIZE', 'LOSS', 'SCHED', 'REDUCTION', 'EPOCHS', 'DROPOUT',
           'LR', 'WD', 'WEIGHT', 'NORMALIZER', 'NORM_VERSION', 'NORM_VERSIONS', 'PRED_LEVELS', 'VERSIONS', 'SCAN']

#Cell
from ..imports import *

#Cell
_PROJECT = Path('/home/DeepLearning/grades_classif')
PROJECT = Path('/work/stages/schwob/grade_classif')
CSVS = PROJECT/'csvs'
LEVEL = 1
_FULL_DATA = Path(f'/data/DeepLearning/SCHWOB_Robin/Patches_256')
FULL_DATA = Path(f'/work/stages/schwob/Patches_256')
DATA = FULL_DATA/f'Patches_MGI_256_{LEVEL}'
DATA_CSV = CSVS/f'scans.csv'
_MODELS = Path('/data/DeepLearning/SCHWOB_Robin/models/logs')
MODELS = PROJECT/'models/logs'
NORM_CSV = CSVS/'categories.csv'
CONCEPTS = CSVS/f'concepts_{LEVEL}.csv'
_CONCEPTS = None
CONCEPT_CLASSES = CSVS/'concept_classes.csv'
_CONCEPT_CLASSES = None
MODEL = 'resnet18'
GPUS = [0]
SIZE = 224
BATCH_SIZE = 64
LOSS = 'cross-entropy'
SCHED = 'one-cycle'
REDUCTION = 'mean'
EPOCHS = 50
DROPOUT= 0.5
LR = 1e-3
WD = 0.01
WEIGHT = 10.
NORMALIZER = None
NORM_VERSION = 11
NORM_VERSIONS = [0, 0, 0, 0]
PRED_LEVELS = [1, 3, 5, 7]
VERSIONS = [0, 0, 0, 0]
SCAN = None