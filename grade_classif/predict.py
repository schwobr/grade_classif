#AUTOGENERATED! DO NOT EDIT! File to edit: dev/02_predict.ipynb (unless otherwise specified).

__all__ = ['predict_one_scan_one_level', 'predict_one_scan', 'predict_all']

#Cell
from .core import ifnone
from .data.utils import load_batches
from .models.plmodules import GradesClassifModel
from .data.read import get_scan
from .imports import *

#Cell
def predict_one_scan_one_level(model, fn):
    preds = []
    for x in load_batches(fn, bs=model.bs, device=model.main_device):
        preds.append(model.predict(x).detach().cpu()[:, 1])
    preds = torch.cat(preds)
    return preds.sum().item()/len(preds)

#Cell
def predict_one_scan(hparams):
    preds = []
    for level, version, norm_version in zip(hparams.levels, hparams.versions, hparams.norm_versions):
        hparams.level = level
        hparams.norm_version = norm_version
        model = GradesClassifModel(hparams)
        model.load(version)
        path = get_scan(hparams.full_data/f'{hparams.full_data.name}_{level}', hparams.scan, include=['1', '3'])
        preds.append(predict_one_scan_one_level(model, path))
    preds = torch.cat(preds)
    return preds.sum().item()/len(preds)

#Cell
def predict_all(hparams):
    df = pd.read_csv(hparams.data_csv, header='infer')
    preds = []
    scans = []
    levels = []
    for level, version, norm_version in zip(hparams.levels, hparams.versions, hparams.norm_versions):
        hparams.level = level
        hparams.norm_version = norm_version
        model = GradesClassifModel(hparams)
        model.load(version)
        for row in tqdm(df.loc[df['split']=='valid'].values):
            scan, grade = row[:-1]
            fn = hparams.full_data/f'{hparams.full_data.name}_{level}'/str(grade)/scan
            try:
                preds.append(predict_one_scan_one_level(model, fn))
            except FileNotFoundError:
                continue
            scans.append(scan)
            levels.append(level)
    res = pd.DataFrame({'level': levels, 'scan': scans, 'pred': preds})
    return res