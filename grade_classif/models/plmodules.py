#AUTOGENERATED! DO NOT EDIT! File to edit: dev/20_models.plmodules.ipynb (unless otherwise specified).

__all__ = ['BaseModule', 'GradesClassifModel', 'Normalizer']

#Cell
import pytorch_lightning as pl
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import OneCycleLR, CosineAnnealingLR, ReduceLROnPlateau
from ..data.dataset import ImageClassifDataset, NormDataset
from ..data.transforms import get_transforms
from ..data.utils import show_img
from .utils import named_leaf_modules, get_sizes, get_num_features
from .modules import DynamicUnet, bn_drop_lin
from ..core import ifnone
import timm
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

#Cell
def _get_loss(loss_name, weight, reduction, device='cpu'):
    if loss_name == 'cross-entropy':
        loss = nn.CrossEntropyLoss(torch.tensor([weight, 1.], device=device), reduction=reduction)
    if loss_name == 'mse':
        loss = nn.MSELoss(reduction=reduction)
    return loss.__call__

#Cell
def _get_scheduler(opt, name, total_steps, lr):
    if name == 'one-cycle':
        sched = OneCycleLR(opt, lr, total_steps=total_steps)
        sched.step_on_batch = True
    elif name == 'cosine-anneal':
        sched = CosineAnnealingLR(opt, total_steps)
        sched.step_on_batch = True
    elif name == 'reduce-on-plateau':
        sched= ReduceLROnPlateau(opt)
        sched.step_on_batch = False
    else:
        sched = None
    return sched

#Cell
class BaseModule(pl.LightningModule):
    def __init__(self, hparams, metrics=None):
        super(BaseModule, self).__init__()
        self.hparams = hparams
        self.main_device = 'cpu' if hparams.gpus is None else f'cuda:{hparams.gpus[0]}'
        try:
            weight = hparams.weight
        except AttributeError:
            weight = 1.
        self.loss = _get_loss(hparams.loss, weight, hparams.reduction, device=self.main_device)
        self.bs = hparams.batch_size
        self.lr = hparams.lr
        self.wd = hparams.wd
        self.metrics = ifnone(metrics, [])
        model_type = 'normalizer' if isinstance(self, Normalizer) else 'classifier'
        self.save_path = hparams.savedir/f'level_{hparams.level}/{model_type}/{hparams.model}'

    def post_init(self):
        self.leaf_modules = named_leaf_modules('', self)
        self.sizes = get_sizes(self, input_shape=(3, self.hparams.size, self.hparams.size), leaf_modules=self.leaf_modules)
        self = self.to(self.main_device)

    def training_step(self, batch, batch_nb):
        # REQUIRED
        x, y = batch
        y_hat = self(x)
        loss = self.loss(y_hat, y)
        lr = self.sched.optimizer.param_groups[-1]['lr']
        log = {'train_loss': loss, 'lr': lr}
        for metric in self.metrics:
            try:
                name = metric.__name__
            except AttributeError:
                name = metric.func.__name__
                kws = metric.keywords
                for k in kws:
                    name += f'_{k}{kws[k]}'
            log[name] = metric(y_hat, y)
        return {'loss': loss, 'log': log}


    def validation_step(self, batch, batch_nb):
        # OPTIONAL
        x, y = batch
        y_hat = self(x)
        loss = self.loss(y_hat, y)
        return {'val_loss': loss}


    def validation_end(self, outputs):
        # OPTIONAL
        loss = torch.stack([x['val_loss'] for x in outputs]).mean()
        log = {'val_loss': loss}
        return {'val_loss': loss, 'log': log}


    def test_step(self, batch, batch_nb):
        # OPTIONAL
        x, y = batch
        y_hat = self(x)
        return {'test_loss': self.loss(y_hat, y)}


    def test_end(self, outputs):
        # OPTIONAL
        avg_loss = torch.stack([x['test_loss'] for x in outputs]).mean()
        return {'avg_test_loss': avg_loss}

    def configure_optimizers(self):
        # REQUIRED
        opt = torch.optim.Adam(self.parameters(), lr=self.lr)
        self.sched = _get_scheduler(opt, self.hparams.sched, self.hparams.epochs*len(self.train_dataloader()), self.lr)
        return opt

    def on_after_backward(self):
        for pg in self.sched.optimizer.param_groups:
            for p in pg['params']: p.data.mul_(1 - self.wd*pg['lr'])

    def on_batch_end(self):
        if self.sched is not None and self.sched.step_on_batch:
            self.sched.step()

    def on_epoch_end(self):
        if self.sched is not None and not self.sched.step_on_batch:
            self.sched.step()

    @pl.data_loader
    def train_dataloader(self):
        return DataLoader(self.data.train, batch_size=self.bs, shuffle=True)


    @pl.data_loader
    def val_dataloader(self):
        # OPTIONAL
        # can also return a list of val dataloaders
        return DataLoader(self.data.valid, batch_size=self.bs)

    @pl.data_loader
    def test_dataloader(self):
        # OPTIONAL
        # can also return a list of test dataloaders
        return DataLoader(self.data.test, batch_size=self.bs) if self.data.test is not None else None

    def load(self, version):
        save_dir = self.save_path/f'lightning_logs/version_{version}/checkpoints'
        path = next(save_dir.iterdir())
        checkpoint = torch.load(path, map_location=lambda storage, loc: storage)
        self.load_state_dict(checkpoint['state_dict'])

    def my_summarize(self):
        """
        TODO: change to make it work with `get_size` changes
        """
        summary = pd.DataFrame(self.sizes, columns=['Type', 'Name', 'Output Shape'])
        return summary

    def fit(self):
        trainer = pl.Trainer(gpus=self.hparams.gpus, default_save_path=self.save_path, min_epochs=self.hparams.epochs, max_epochs=self.hparams.epochs)
        self.version = trainer.logger.version
        trainer.fit(self)

    def predict(self, x):
        return self.eval()(x)

#Cell
class GradesClassifModel(BaseModule):
    def __init__(self, hparams):
        super(GradesClassifModel, self).__init__(hparams)
        tfms = get_transforms(hparams.size)
        self.data = (ImageClassifDataset.
                     from_folder(Path(hparams.data), lambda x: x.parts[-3], classes=['1', '3'], extensions=['.png'], include=['1', '3'], open_mode='3G').
                     split_by_csv(hparams.data_csv).
                     to_tensor(tfms=tfms, tfm_y=False))
        base_model = timm.create_model(hparams.model, pretrained=not hparams.rand_weights)
        self.base_model = nn.Sequential(*list(base_model.children())[:-2])
        head = [nn.AdaptiveAvgPool2d(1), nn.Flatten()]
        nf = get_num_features(self.base_model)
        p = hparams.dropout
        head += bn_drop_lin(nf, 512, p=p/2) + bn_drop_lin(512, 2, p=p)
        self.head = nn.Sequential(*head)
        self.post_init()
        self.create_normalizer()

    def create_normalizer(self):
        hparams = self.hparams
        if hparams.normalizer is not None:
            norm = DynamicUnet(hparams.normalizer, n_classes=3, input_shape=(3, hparams.size, hparams.size), pretrained=True)
            if hparams.norm_version is not None:
                save_dir = self.save_path.parents[1]/'normalizer'/f'{hparams.normalizer}/lightning_logs/version_{hparams.norm_version}/checkpoints'
                path = next(save_dir.iterdir())
                checkpoint = torch.load(path, map_location=lambda storage, loc: storage)
                state_dict = {}
                for k in checkpoint['state_dict']:
                    state_dict[k.replace('unet.', '')] = checkpoint['state_dict'][k]
                norm.load_state_dict(state_dict)
                for p in norm.parameters():
                    p.requires_grad = False
            norm = norm.to(self.main_device)
            self.norm = norm.__call__

    def forward(self, x):
        if hasattr(self, 'norm'):
            x = self.norm(x)
        x = self.base_model(x)
        x = self.head(x)
        return x

#Cell
class Normalizer(BaseModule):
    def __init__(self, hparams):
        super(Normalizer, self).__init__(hparams)
        input_shape = (3, hparams.size, hparams.size)
        self.unet = DynamicUnet(hparams.normalizer, n_classes=3, input_shape=input_shape, pretrained=not hparams.rand_weights)
        # meta = cnn_config(resnet34)
        # body = create_body(resnet34, True, None)
        # size = (224, 224)
        # self.unet = models.unet.DynamicUnet(body, n_classes=3, img_size=size, blur=False, blur_final=True,
        #      self_attention=False, y_range=None, norm_type=NormType, last_cross=True,
        #      bottle=False)
        tfms = get_transforms(hparams.size)
        self.data = (NormDataset.
                     from_folder(Path(hparams.data), lambda x: x, hparams.csv, extensions=['.png'], include=['1', '3']).
                     split_by_csv(hparams.data_csv).
                     to_tensor(tfms=tfms))
        self.post_init()


    def forward(self, x):
        return self.unet(x)


    def show_results(self, n=16, random=False, imgsize=4, title=None, **kwargs):
        n = min(n, self.bs)
        fig, axs = plt.subplots(n, 3, figsize=(imgsize*3, imgsize*n))
        idxs = np.random.choice(np.arange(len(self.data.valid)), size=n, replace=False)
        inputs = []
        targs = []
        for idx in idxs:
            x, y = self.data.valid[idx]
            inputs.append(x)
            targs.append(y)
        inputs = torch.stack(inputs).to(next(self.parameters()).device)
        preds = self.eval()(inputs).clamp(0, 1)
        for ax_r, x, y, z in zip(axs, inputs, targs, preds):
            x = x.cpu().numpy().transpose(1, 2, 0)
            y = y.numpy().transpose(1, 2, 0)
            z = z.detach().cpu().numpy().transpose(1, 2, 0)
            show_img(x, ax=ax_r[0])
            show_img(y, ax=ax_r[1])
            show_img(z, ax=ax_r[2])
        title = ifnone(title, 'input/target/prediction')
        fig.suptitle(title)
        plt.show()

    def freeze_encoder(self):
        for m in self.leaf_modules('', self):
            if 'encoder' in m.name and not isinstance(m, nn.BatchNorm2d):
                for param in m.parameters():
                    param.requires_grad = False

    def init_bn(self):
        for m in self.modules():
            if isinstance(m, nn.BatchNorm2d):
                with torch.no_grad():
                    m.bias.fill_(1e-3)
                    m.weight.fill_(1.)