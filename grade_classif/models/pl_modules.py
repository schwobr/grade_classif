#AUTOGENERATED! DO NOT EDIT! File to edit: dev/20_models_pl_modules.ipynb (unless otherwise specified).

__all__ = ['BaseModule', 'GradesClassifModel', 'Normalizer']

#Cell
import pytorch_lightning as pl
import torch
import torch.nn as nn
from torch.optim.lr_scheduler import OneCycleLR, CosineAnnealingLR, ReduceLROnPlateau
from ..data.dataset import ImageClassifDataset, NormDataset
from ..data.transforms import get_transforms
from .utils import named_leaf_modules, get_sizes
from .unet import DynamicUnet
from ..core import ifnone
import timm
from pathlib import Path

#Cell
def _get_loss(loss_name, weight, reduction):
    if loss_name == 'cross-entropy':
        loss = nn.CrossEntropyLoss(torch.tensor([weight, 1.]), reduction=reduction)
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
    def __init__(self, hparams):
        super(BaseModule, self).__init__()
        self.hparams = hparams
        self.loss = _get_loss(hparams.loss, hparams.weight, hparams.reduction)
        self.bs = hparams.batch_size
        self.lr = hparams.lr
        self.wd = hparams.wd

    def post_init(self):
        self.leaf_modules = named_leaf_modules('', self)
        self.sizes = get_sizes(self, input_shape=(3, self.hparams.size, self.hparams.size), leaf_modules=self.leaf_modules)

    def training_step(self, batch, batch_nb):
        # REQUIRED
        x, y = batch
        y_hat = self(x)
        loss = self.loss(y_hat, y)
        lr = self.sched.optimizer.param_groups[-1]['lr']
        log = {'train_loss': loss, 'lr': lr}
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
        self.sched = _get_scheduler(opt, self.hparams.sched, self.lr, self.hparams.epochs*len(self.train_dataloader()))
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
        save_dir = hparams.savedir/f'lightning_logs/version_{version}/checkpoints'
        path = next(save_dir.iterdir())
        checkpoint = torch.load(path, map_location=lambda storage, loc: storage)
        self.load_state_dict(checkpoint['state_dict'])

    def my_summarize(self):
        summary = pd.DataFrame(self.sizes, columns=['Type', 'Name', 'Output Shape'])
        return summary

    def fit(self, epochs=None, gpus=[0]):
        epochs = ifnone(epochs, self.hparams.epochs)
        trainer = pl.Trainer(gpus=gpus, default_save_path=self.hparams.savedir, min_nb_epochs=epochs, max_nb_epochs=epochs)
        trainer.fit(self)

#Cell
class GradesClassifModel(BaseModule):
    def __init__(self, hparams):
        super(GradesClassifModel, self).__init__(hparams)
        tfms = get_transforms(hparams.size)
        self.data = (ImageClassifDataset.
                     from_folder(Path(hparams.data), lambda x: x.parts[-3], classes=['1', '3'], extensions=['.png'], include=['train', 'valid']).
                     split_by_folder().
                     to_tensor(tfms=tfms, tfm_y=False))
        base_model = timm.create_model(hparams.model, pretrained=True)
        self.base_model = nn.Sequential(*list(base_model.children())[:-2])
        head = [nn.AdaptiveAvgPool2d(1), nn.Flatten()]
        nf = get_num_features(self.base_model)
        p = hparams.dropout
        head += bn_drop_lin(nf, 512, p=p/2) + bn_drop_lin(512, 2, p=p)
        self.head = nn.Sequential(*head)
        self.post_init()

    def forward(self, x):
        x = self.base_model(x)
        x = self.head(x)
        return x

#Cell
class Normalizer(BaseModule):
    def __init__(self, hparams):
        super(Normalizer, self).__init__(hparams)
        input_shape = (3, hparams.size, hparams.size)
        self.unet = DynamicUnet(hparams.model, n_classes=3, input_shape=input_shape, pretrained=hparams.pretrained)
        # meta = cnn_config(resnet34)
        # body = create_body(resnet34, True, None)
        # size = (224, 224)
        # self.unet = models.unet.DynamicUnet(body, n_classes=3, img_size=size, blur=False, blur_final=True,
        #      self_attention=False, y_range=None, norm_type=NormType, last_cross=True,
        #      bottle=False)
        tfms = get_transforms(hparams.size)
        self.data = (NormDataset.
                     from_folder(Path(hparams.data), lambda x: x, hparams.csv, extensions=['.png'], include=['train', 'valid']).
                     split_by_folder().
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
        for n, m in self.leaf_modules('', self):
            if 'encoder' in n and not isinstance(m, nn.BatchNorm2d):
                for param in m.parameters():
                    param.requires_grad = False

    def init_bn(self):
        for m in self.modules():
            if isinstance(m, nn.BatchNorm2d):
                with torch.no_grad():
                    m.bias.fill_(1e-3)
                    m.weight.fill_(1.)