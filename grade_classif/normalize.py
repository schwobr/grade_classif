#AUTOGENERATED! DO NOT EDIT! File to edit: dev/_normalize.ipynb (unless otherwise specified).

__all__ = ['DATA', 'INFOLDER', 'OUTFOLDER', 'MODEL', 'VERSION', 'BATCH_SIZE', 'OPEN_MODE', 'GPU', 'parser', 'args',
           'device', 'ds', 'norm', 'dl', 'load_paths']

#Cell
from .imports import *
from .data.dataset import NormDataset
from .models.modules import DynamicUnet
from argparse import ArgumentParser
from shutil import copy

#Cell
DATA = Path('/data/DeepLearning/SCHWOB_Robin')
INFOLDER = DATA/'Patches_299/Patches_299_1'
OUTFOLDER = DATA/'Patches_normalized_299/Patches_normalized_299_1'
MODEL = 'cbr_3_32_4'
VERSION = 'b60122c635714bd9a7fda47e7b89cf6b'
BATCH_SIZE = 32
OPEN_MODE = 'RGB'
GPU = 0

#Cell
parser = ArgumentParser()

#Cell
parser.add_argument('--file', '-f', help='notebook convenience')
parser.add_argument('--HistoryManager.hist_file', help='nbconvert convenience')
parser.add_argument('--infolder', default=INFOLDER, help="folder containing patches to normalize")
parser.add_argument('--outfolder', default=OUTFOLDER, help="output folder to store normalized patches in")
parser.add_argument('--model', default=MODEL, help="encoder for the normalizer")
parser.add_argument('--version', default=VERSION, help="version of the normalizer to load")
parser.add_argument('--batch-size', type=int, default=BATCH_SIZE, help="size of the batches to load into GPU")
parser.add_argument('--open-mode', choices=['RGB', '3G'], default=OPEN_MODE, help="how the image should be opened (3G for gray and RGB for color)")
parser.add_argument('--gpu', type=int, default=GPU, help="GPU device to tuse")

#Cell
args = parser.parse_args()

#Cell
device = torch.device(f'cuda:{args.gpu}')

#Cell
ds = (NormDataset.
      from_folder(args.infolder, extensions=['.png'], open_mode=args.open_mode).
      to_tensor())

#Cell
norm = DynamicUnet(args.model, 3, ds[0][0].shape, False).eval().to(device)

#Cell
for p in norm.parameters():
    p.requires_grad = False

#Cell
dl = torch.utils.data.DataLoader(ds, batch_size=args.batch_size)

#Cell
def load_paths(path_list, bs=8):
    for i in range(len(path_list[::bs])):
        yield path_list[bs*i:bs*(i+1)]

#Cell
for (x, _), paths in tqdm_notebook(zip(dl, load_paths(ds.items, bs=args.batch_size)), total=len(dl)):
    x = x.to(device)
    y = norm(x).detach().cpu().numpy()
    y = y.transpose(0, 2, 3, 1)
    y = (y * 255).astype(np.uint8)
    for img, path in zip(y, paths):
        out_path = Path(args.outfolder)/path.relative_to(args.infolder)
        if out_path.is_file():
            continue
        if not out_path.parent.is_dir():
            out_path.parent.mkdir(parents=True)
        cv2.imwrite(str(out_path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))