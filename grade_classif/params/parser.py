# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/81_params.parser.ipynb (unless otherwise specified).

__all__ = ['hparams']

# Cell
from .defaults import *
import os
from argparse import ArgumentParser

# Cell
_parser = ArgumentParser()
_parser.add_argument('--file', '-f', help='notebook convenience')
_parser.add_argument('--HistoryManager.hist_file', help='nbconvert convenience')
_parser.add_argument('--sched', default=SCHED, choices=['one-cycle', 'cosine-anneal', 'reduce-on-plateau', 'none'], help='scheduler for the optimizer')
_parser.add_argument('--datafolder', default=DATA, help='path to folder containing data')
_parser.add_argument('--data-csv', default=DATA_CSV, help='path to csv listing scans with their grades and split')
_parser.add_argument('--patch-classes', default=PATCH_CLASSES, help='path to csv giving a class for each patch.')
_parser.add_argument('--level', default=LEVEL, type=int, help='zoom level to work on')
_parser.add_argument('--resume-version', default=RESUME, help='version of model to load before training')
_parser.add_argument('--resume-checkpoint', default=None, help='checkpoint to load from when resuming.')
_parser.add_argument('--batch-size', default=BATCH_SIZE, type=int, help='batch size')
_parser.add_argument('--size', default=SIZE, type=int, help='size of the image (as an integer, image is supposed to be square)')
_parser.add_argument('--loss', default=LOSS, choices=['cross-entropy', 'mse', 'focal'], help='loss function')
_parser.add_argument('--savedir', default=MODELS, help='directory to save models and logs in')
_parser.add_argument('--model', default=MODEL, help='name of the base architecture to use for classification')
_parser.add_argument('--normalizer', default=NORMALIZER, help='path to normalizer file as torchscript module')
_parser.add_argument('--rand-weights', action='store_true', help='specify to avoid using a pretrained model for training')
_parser.add_argument('--gpus', default=GPUS, nargs='*', type=int, help='list of gpus you want to use for training (as numbers)')
_parser.add_argument('--reduction', default=REDUCTION, choices=['mean', 'sum', 'none'], help='reduction to apply to loss')
_parser.add_argument('--epochs', default=EPOCHS, type=int, help='number of epochs')
_parser.add_argument('--weights', type=float, nargs="*", default=None, help='weights for cross-entropy loss.')
_parser.add_argument('--dropout', default=DROPOUT, type=float, help='dropout value')
_parser.add_argument('--lr', default=LR, type=float, help='learning rate')
_parser.add_argument('--wd', type=float, default=WD, help='weight decay')
_parser.add_argument('--sample-mode', type=int, default=SAMPLE_MODE, choices=[0, 1, 2], help='type 0 for regular sampling, 1 for oversampling, 2 for undersampling')
_parser.add_argument('--transforms', type=int, default=TRANSFORMS, choices=[0, 1, 2, 3, 4, 5], help='0 means no transform, above enables use of function `get_transformX` with X the number entered.')
_parser.add_argument('--filt', default=FILT, choices=['K', 'K_inter', 'out', 'all', 'K_all'], help='patches to filter depending on their corresponding concept')
_parser.add_argument('--open-mode', default=OPEN_MODE, choices=['3G', 'RGB', 'H', 'E', 'HEG'], help='How the image should be opened (3G for grayscale and RGB for color)')
_parser.add_argument('--train-percent', default=TRAIN_PERCENT, type=float, help='Portion of the training set to run fit on.')
_parser.add_argument('--topk', default=TOPK, type=int, help='Number of patches per slide to train on for MIL.')
_parser.add_argument('--coord-csv', default=COORD_CSV, help='path to csv containing coordinates for each patch to extract from all slides.')
_parser.add_argument('--patches-per-slide', type=int, default=10, help='number of patches to select for each slide when using RNN aggregator on MIL.')
_parser.add_argument('--rnn-hidden-dims', type=int, default=128, help='size of hidden representation in RNN aggregator.')
_parser.add_argument('--profiler', default=None, choices=['simple', 'advanced'], help='type of profiler to use from pytorch_lightning.profiler.')
_parser.add_argument('--mixed-precision', action="store_true", help="specify to use mixed precision training.")
_parser.add_argument('--forget-rate', type=float, default=0.5, help='maximum part of the training set to drop for co-teaching.')
_parser.add_argument('--forget-steps', type=int, default=10, help='number of epochs before getting to maximum forget rate.')
_parser.add_argument('--disagree-only', action='store_true', help='specify to only train co-teaching models on data that is disagreed upon.')
_parser.add_argument('--max-patches-per-slide', type=int, default=None, help='maximum number of patches from each slide to use for training.')
_parser.add_argument('--glimpse-size', type=int, default=256, help='size of glimpse image for RNN attention.')
_parser.add_argument('--n-glimpses', type=int, default=3, help='number of glimpses to observe in RNN attention.')
_parser.add_argument('--gamma', type=float, default=1, help='gamma parameter for RNN attention.')
_parser.add_argument('--auto-lr-find', action='store_true', help='specify to run a lr finder before training.')
_parser.add_argument('--pacs-filt', default=None, choices=['4', '5', '8', '45', '48', '58'], help='specify a PACS datasets to use, use all otherwise.')
_parser.add_argument('--norm-ref', default='/data/DeepLearning/SCHWOB_Robin/CF_Normacolor_0182_41472_67392.png', help='path to reference image for staintools image normalization methods.')
_parser.add_argument('--norm-method', default=None, choices=['reinhard', 'vahadane', 'macenko'], help='staintool normalization method to use.')
_parser.add_argument('--num-workers', default=4, type=int, help='number of cpu workers to use for data loading.')
_parser.add_argument('--embed-dim', default=2048, type=int, help='size of feature vector for WSITransformer.')
_parser.add_argument('--padding-file', default='/data/DeepLearning/SCHWOB_Robin/padding_2048_1024_1.npy', help='path to file containing feature vector to use for padding in WSITransformer.')
_parser.add_argument('--deepspeed', action='store_true', help='specify to enable deepspeed plugin. Will also enable mixed precision by default.')

# Cell
hparams = _parser.parse_args()

# Cell
#os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
#os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(map(str, hparams.gpus))