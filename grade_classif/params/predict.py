#AUTOGENERATED! DO NOT EDIT! File to edit: dev/83_params_predict.ipynb (unless otherwise specified).

__all__ = ['hparams']

#Cell
from test_tube import HyperOptArgumentParser
from test_tube.argparse_hopt import TTNamespace
from .defaults import *
from pathlib import Path

#Cell
def _getattr(self, name):
    return None
TTNamespace.__getattr__ = _getattr

#Cell
_parser = HyperOptArgumentParser(strategy='random_search')
_parser.add_argument('--file', '-f', help='notebook convenience')
_parser.add_argument('--HistoryManager.hist_file', help='nbconvert convenience')
_parser.add_argument('--data', default=FULL_DATA, help='path to folder containing data')
_parser.add_argument('--data-csv', default=DATA_CSV, help='path to csv listing scans with their grades and split')
_parser.add_argument('--scan', default=SCAN, help='name of scan to predict. If not specified, all valid scans are predicted')
_parser.add_argument('--levels', default=PRED_LEVELS, type=int, help='zoom levels to work on')
_parser.add_argument('--batch-size', default=BATCH_SIZE, type=int, help='batch size')
_parser.add_argument('--size', default=SIZE, type=int, help='size of the image (as an integer, image is supposed square)')
_parser.add_argument('--loss', default=LOSS, choices=['cross-entropy', 'mse'], help='loss function')
_parser.add_argument('--savedir', default=MODELS, type=Path, help='directory to save models and logs in')
_parser.add_argument('--normalizer', default=NORMALIZER, help='encoder of the normalizer to use for classification')
_parser.add_argument('--norm-version', default=NORM_VERSION, type=int, help='version of the encoder to load for classification')
_parser.add_argument('--versions', default=VERSIONS, type=int, nargs='*', help='list of model versions to use. Must specify one for each level the in same order.')
_parser.add_argument('--gpus', default=GPUS, nargs='*', type=int, help='list of gpus you want to use for training (as numbers)')
_parser.add_argument('--reduction', default=REDUCTION, choices=['mean', 'sum', 'none'], help='reduction to apply to loss')
_parser.opt_range('--dropout', default=DROPOUT, type=float, tunable=True, low=0., high=0.8, nb_samples=5, help='dropout value')
_parser.opt_list('--model', default=MODEL, tunable=True, options=['resnet34', 'resnet50', 'efficientnet_b1'], help='name of the base architecture to use for training')
_parser.opt_range('--weight', type=float, tunable=True, default=WEIGHT, low=1., high=10., nb_samples=8, help='weight to give to grade 1 (grade 3 being weighted to 1)')

#Cell
hparams = _parser.parse_args()