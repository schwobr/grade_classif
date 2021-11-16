# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_train.ipynb (unless otherwise specified).

__all__ = ['train_normalizer', 'train_classifier', 'train_transformer', 'train_rnn_attention', 'train_reargmt',
           'train_FLFH', 'train_discriminator', 'train_cancer_detector', 'train_bach', 'train_mil_cancer_detector',
           'train_mil_reargmt', 'train_rnn_reargmt']

# Cell
from .imports import *
from pytorch_lightning.metrics import Accuracy

from .data.modules import (
    ImageClassifDataModule,
    MILDataModule,
    NormDataModule,
    RNNAggDataModule,
    FeaturesClassifDataModule
)
from .models.plmodules import (
    ImageClassifModel,
    MILModel,
    Normalizer,
    RNNAggregator,
    RNNAttention,
    WSITransformer
)

# Cell
def train_normalizer(hparams: Namespace) -> Normalizer:
    hparams = vars(hparams)
    dm = NormDataModule(**hparams)
    model = Normalizer(**hparams)
    # model.freeze_encoder()
    model.fit(dm)
    return model

# Cell
def train_classifier(hparams: Namespace) -> ImageClassifModel:
    hparams = vars(hparams)
    classes = ["1", "3"]
    dm = ImageClassifDataModule(
        classes=classes, label_func=lambda x: x.parts[-3], include=classes, **hparams
    )
    model = ImageClassifModel(classes=classes, n_classes=len(classes), **hparams)
    model.fit(dm, monitor="AUC_3")
    return model

# Cell
def train_transformer(hparams: Namespace) -> ImageClassifModel:
    hparams = vars(hparams)
    classes = ["1", "3"]
    dm = FeaturesClassifDataModule(classes=classes, get_id=lambda x: x.name, label_func=lambda x: x.parts[-2], **hparams)
    model = WSITransformer(
        classes=classes,
        n_classes=len(classes),
        **hparams
    )
    model.fit(dm, monitor="AUC_3")
    return model

# Cell
def train_rnn_attention(hparams: Namespace) -> RNNAttention:
    hparams = vars(hparams)
    classes = ["1", "3"]
    dm = ImageClassifDataModule(classes=classes, label_func=lambda x: x.parts[-3], **hparams)
    model = RNNAttention(
        classes=classes,
        n_classes=len(classes),
        **hparams
    )
    model.fit(dm)
    return model

# Cell
def train_reargmt(hparams: Namespace) -> ImageClassifModel:
    classes = ["NoReargmt", "DHL_THL"]
    def _label_func(x):
        return x.parts[-3]
    hparams = vars(hparams)
    dm = ImageClassifDataModule(classes=classes, label_func=_label_func, **hparams)
    model = ImageClassifModel(
        classes=classes,
        n_classes=len(classes),
        **hparams
    )
    model.fit(dm)
    return model

# Cell
def train_FLFH(hparams: Namespace) -> ImageClassifModel:
    classes = ["FH", "FL"]
    def _label_func(x):
        return x.parts[-3]
    hparams = vars(hparams)
    dm = ImageClassifDataModule(classes=classes, label_func=_label_func, **hparams)
    model = ImageClassifModel(
        classes=classes,
        n_classes=len(classes),
        **hparams
    )
    model.fit(dm)
    return model

# Cell
def train_discriminator(hparams: Namespace) -> ImageClassifModel:
    classes = ["04", "05", "08"]

    def _label_func(x):
        for cl in classes:
            if f"PACS{cl}" in x.name:
                return cl

    hparams = vars(hparams)
    dm = ImageClassifDataModule(
        classes=classes, label_func=_label_func, include=["1", "3"], **hparams
    )
    model = ImageClassifModel(classes=classes, n_classes=len(classes), **hparams)
    model.fit(dm)
    return model

# Cell
def train_cancer_detector(hparams: Namespace) -> ImageClassifModel:
    hparams = vars(hparams)
    classes = ["artefact", "cancer", "non_cancer"]
    dm = ImageClassifDataModule(
        classes=classes,
        label_func=lambda x: x.parent.name,
        get_id=lambda x: "_".join(x.name.split("_")[:-2]),
        **hparams
    )
    model = ImageClassifModel(
        classes=classes,
        n_classes=len(classes),
        **hparams
    )
    model.fit(dm, monitor="f_1_cancer")
    return model

# Cell
def train_bach(hparams: Namespace) -> ImageClassifModel:
    hparams = vars(hparams)
    classes = ["non_carcinoma", "carcinoma"]
    dm = ImageClassifDataModule(
        classes=classes,
        label_func=lambda x: x.parent.name,
        get_id=lambda x:x.name.split("_")[0],
        **hparams
    )
    model = ImageClassifModel(
        classes=classes,
        n_classes=len(classes),
        **hparams
    )
    model.fit(dm, monitor="AUC_carcinoma")
    return model

# Cell
def train_mil_cancer_detector(hparams: Namespace) -> MILModel:
    hparams = vars(hparams)
    dm = MILDataModule(classes=["None", "Infilt"], **hparams)
    model = MILModel(
        **hparams
    )
    model.fit(dm, num_sanity_val_steps=0, reload_dataloaders_every_epoch=True)
    return model

# Cell
def train_mil_reargmt(hparams: Namespace) -> MILModel:
    hparams = vars(hparams)
    dm = MILDataModule(
        classes=["NoReargmt", "DHL_THL"],
        extensions=[".mrxs", ".svs"],
        label_func=lambda x: x.parts[-3],
        **hparams
    )
    model = MILModel(
        **hparams
    )
    model.fit(
        dm,
        num_sanity_val_steps=0,
        reload_dataloaders_every_epoch=True,
        check_val_every_n_epochs=5,
    )
    return model

# Cell
def train_rnn_reargmt(hparams: Namespace) -> RNNAggregator:
    hparams = vars(hparams)
    classes = ["NoReargmt", "DHL_THL"]
    dm = RNNAggDataModule(
        classes=classes,
        extensions=[".mrxs", ".svs"],
        label_func=lambda x: x.parts[-3],
        **hparams
    )
    model = RNNAggregator(
        classes=classes,
        **hparams,
        metrics=[accuracy, precision, recall, f_1]
    )
    model.fit(
        dm,
        log_every_n_steps=5
    )
    return model