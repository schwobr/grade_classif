#AUTOGENERATED! DO NOT EDIT! File to edit: dev/12_data.dataset.ipynb (unless otherwise specified).

__all__ = ['MyDataset', 'ClassDataset', 'ImageClassifDataset', 'ImageSegmentDataset', 'NormDataset', 'SplitDataset',
           'TensorDataset']

#Cell
from .loaders import ImageLoader, MaskLoader, CategoryLoader
from .utils import show_img, np_to_tensor
from .read import get_items
from ..core import ifnone
from ..imports import *
from albumentations import Compose
from torch.utils.data import Dataset

#Cell
class MyDataset(Dataset):
    """
    """
    def __init__(self, items, labels, item_loader, label_loader):
        super().__init__()
        self.items = np.array(items)
        self.labels = np.array(labels)
        self.item_loader = item_loader
        self.label_loader = label_loader

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        item, label = self.items[i], self.labels[i]
        x = self.item_loader(item)
        y = self.label_loader(label)
        return x, y

    @classmethod
    def from_folder(cls, folder, label_func, item_loader, label_loader, after_open=None, recurse=True, extensions=None, include=None, exclude=None):
        """
        Creates a `MyDataset` object by reading files from a folder. It uses `get_item` and therefore works the same.
        """
        folder = Path(folder)
        items, labels = get_items(folder, label_func, recurse=recurse, extensions=extensions, include=include, exclude=exclude)
        return cls(items, labels, item_loader, label_loader)

    def to_tensor(self, tfms=None, tfm_y=True):
        """
        Creates a `TensorDataset` based on this dataset.
        """
        return TensorDataset(self, tfms=tfms, tfm_y=tfm_y)

    def split_by_list(self, train, valid, test=None):
        """
        Creates a `SplitDataset` using `train`, `valid` and optionally `test` tuples. Each tuple contains 2 lists: one for items and one for labels.
        """
        return SplitDataset(self.__class__(train[0], train[1], self.item_loader, self.label_loader),
                            self.__class__(valid[0], valid[1], self.item_loader, self.label_loader),
                            None if test is None else self.__class__(test[0], test[1], self.item_loader, self.label_loader))

    def split_by_folder(self):
        """
        Creates a `SplitDataset` by looking for `ŧrain`, `valid` and `test` in item paths and splitting the dataset accordingly.
        """
        train = ([], [])
        valid = ([], [])
        test = ([], [])
        for item, label in zip(self.items, self.labels):
            if 'train' in item.parts:
                train[0].append(item)
                train[1].append(label)
            elif 'valid' in item.parts:
                valid[0].append(item)
                valid[1].append(label)
            elif 'test' in item.parts:
                test[0].append(item)
                test[1].append(label)
        if test[0] == []:
            test = None
        return self.split_by_list(train, valid, test)

    def split_by_csv(self, csv, split_column='split', id_column='scan', get_id=None):
        """
        Creates a `SplitDataset` by using a csv that contains an `id_column` column for identifying items
        and a `split_column` column that contains either `'train'`, `'valid'` or `'test'`. `get_id` is the
        function used to extract the item's id from the item itself. By default it considers that `item` is a
        `Path` object and takes the parent folder's name as id.
        """
        get_id = ifnone(get_id, lambda x: x.parent.name)
        df = pd.read_csv(csv, header='infer')
        train = ([], [])
        valid = ([], [])
        test = ([], [])
        train_ids = df.loc[df[split_column] == 'train', id_column]
        valid_ids = df.loc[df[split_column] == 'valid', id_column]
        test_ids = df.loc[df[split_column] == 'test', id_column]
        for item, label in zip(self.items, self.labels):
            item_id = get_id(item)
            if item_id in train_ids.values:
                train[0].append(item)
                train[1].append(label)
            elif item_id in valid_ids.values:
                valid[0].append(item)
                valid[1].append(label)
            elif item_id in test_ids.values:
                test[0].append(item)
                test[1].append(label)
        if test[0] == []:
            test = None
        return self.split_by_list(train, valid, test)

#Cell
class ClassDataset(MyDataset):
    def __init__(self, *args, n_classes=2, **kwargs):
        super().__init__(*args, **kwargs)
        self.n_classes = n_classes

#Cell
class ImageClassifDataset(ClassDataset):
    def show(self, k, ax=None, figsize=(3,3), hide_axis=True, cmap='viridis', **kwargs):
        """
        Shows the `k`th image from the dataset with the corresponding label.
        """
        x, y  = self[k]
        y = self.label_loader.classes[y]
        ax = show_img(x, ax=ax, hide_axis=hide_axis, cmap=cmap, figsize=figsize, title=str(y), **kwargs)

    def show_rand(self, ax=None, figsize=(3,3), hide_axis=True, cmap='viridis', **kwargs):
        """
        Shows a random image from the dataset with the corresponding label.
        """
        k = random.randint(0, len(self)-1)
        self.show(k, ax=ax, figsize=figsize, hide_axis=hide_axis, cmap=cmap, **kwargs)

    @classmethod
    def from_folder(cls, folder, label_func, n_classes=None, classes=None, recurse=True, extensions=None, include=None, exclude=None, **kwargs):
        """
        Overwrites `MyDataset.from_folder`. Works basically the same but you don't need to pass loaders, but instead `n_classes`
        or `classes` arguments. Loaders are automatically created using these.
        """
        folder = Path(folder)
        items, labels = get_items(folder, label_func, recurse=recurse, extensions=extensions, include=include, exclude=exclude)
        return cls(items, labels, ImageLoader(**kwargs), CategoryLoader(n_classes, classes), n_classes=ifnone(n_classes, len(classes)))

#Cell
class ImageSegmentDataset(ClassDataset):
    def show(self, k, ax=None, figsize=(3,3), title=None, hide_axis=True, cmap='tab20', **kwargs):
        """
        Shows the `k`th image from the dataset with the corresponding mask above it.
        """
        x, y  = self[k]
        ax = show_img(x, ax=ax, hide_axis=hide_axis, cmap=cmap, figsize=figsize, **kwargs)
        ax = show_img(y, ax=ax, hide_axis=hide_axis, cmap=cmap, figsize=figsize,
                        interpolation='nearest', alpha=alpha, vmin=0, title=title, **kwargs)

    def show_rand(self, ax=None, figsize=(3,3), hide_axis=True, cmap='tab20', **kwargs):
        """
        Shows a random image from the dataset withthe corresponding mask above it.
        """
        k = random.randint(0, len(self)-1)
        self.show(k, ax=ax, figsize=figsize, hide_axis=hide_axis, cmap=cmap, **kwargs)

    @classmethod
    def from_folder(cls, folder, label_func, n_classes=None, classes=None, recurse=True, extensions=None, include=None, exclude=None):
        """
        Same as `ImageClassifDataset.from_folder`.
        """
        folder = Path(folder)
        items, labels = get_items(folder, label_func, recurse=recurse, extensions=extensions, include=include, exclude=exclude)
        return cls(items, labels, ImageLoader(), MaskLoader(), n_classes=ifnone(n_classes, len(classes)))

#Cell
class NormDataset(MyDataset):
    def show(self, k, axs=None, figsize=(5, 5), title=None, hide_axis=True, cmap='viridis', **kwargs):
        """
        Shows the `k`th image from the dataset as grayscale and colored.
        """
        x, y  = self[k]
        axs = ifnone(axs, plt.subplots(1, 2, figsize=figsize)[1])
        ax = show_img(x, ax=axs[0], hide_axis=hide_axis, cmap=cmap, figsize=figsize, **kwargs)
        ax = show_img(y, ax=axs[1], hide_axis=hide_axis, cmap=cmap, figsize=figsize, **kwargs)

    def show_rand(self, axs=None, figsize=(5, 5), hide_axis=True, cmap='viridis', **kwargs):
        """
        Shows a random image from the dataset as grayscale and colored.
        """
        k = random.randint(0, len(self)-1)
        self.show(k, axs=axs, figsize=figsize, hide_axis=hide_axis, cmap=cmap, **kwargs)

    @classmethod
    def from_folder(cls, folder, csv, id_column='scan', recurse=True, extensions=None, include=None, exclude=None):
        """
        Overwrites `MyDataset.from_folder` so that it doesn't need the loaders or a `label_func`. It howevers requires a `csv`
        argument that contains an `id_column` column to identify images and a `'category'` column that contains 1 if the image
        is to be used for normalization.
        """
        def _label_func(x):
            return x
        df = pd.read_csv(csv)
        vals = df.loc[df['category'] == 1, id_column].values
        def filt(fn):
            return fn.parent.stem in vals
        folder = Path(folder)
        items, labels = get_items(folder, _label_func, recurse=recurse, extensions=extensions, include=include, exclude=exclude, filterfunc=filt)
        return cls(items, labels, ImageLoader(open_mode='3G'), ImageLoader())

#Cell
@dataclass
class SplitDataset:
    """
    """
    train: Dataset
    valid: Dataset
    test: Dataset = None

    def to_tensor(self, tfms=None, tfm_y=True, test_tfms=None):
        """
        Transforms all datasets into `TensorDataset` objects
        """
        tfms = ifnone(tfms, (None, None))
        self.train = self.train.to_tensor(tfms=tfms[0], tfm_y=tfm_y)
        self.valid = self.valid.to_tensor(tfms=tfms[1], tfm_y=tfm_y)
        if self.test is not None:
            self.test = self.test.to_tensor(tfms=test_tfms, tfm_y=tfm_y)
        return self

#Cell
class TensorDataset(Dataset):
    """
    """
    def __init__(self, ds, tfms=None, tfm_y=True):
        self._ds = ds
        self.tfms = ifnone(tfms, [])
        self.tfm_y = tfm_y

    def __len__(self):
        return len(self._ds)

    def __getitem__(self, i):
        x, y = self._ds[i]
        if self.tfms != []:
            aug = Compose(self.tfms)
            augmented = aug(image=x, mask=y if self.tfm_y else None)
            x = augmented['image']
            if self.tfm_y:
                y = augmented['mask']
        x = np_to_tensor(x, type(self._ds.item_loader).__name__.lower().replace('loader', ''))
        y = np_to_tensor(y, type(self._ds.label_loader).__name__.lower().replace('loader', ''))
        return x, y

    def __getattr__(self, name):
        return getattr(self._ds, name)