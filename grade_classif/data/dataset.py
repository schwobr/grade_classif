# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/12_data.dataset.ipynb (unless otherwise specified).

__all__ = ['TestDataset', 'TensorDataset', 'SplitDataset', 'MyDataset', 'ClassDataset', 'ImageClassifDataset',
           'ImageSegmentDataset', 'NormDataset', 'MILDataset', 'RNNSlideDataset']

# Cell
from .loaders import (
    ItemLoader,
    ImageLoader,
    MaskLoader,
    CategoryLoader,
    SlideLoader
)
from .utils import show_img, np_to_tensor
from fastai.data.transforms import get_files
from .transforms import *
from ..core import ifnone
from ..imports import *
from albumentations import Compose, BasicTransform
from torch.utils.data import Dataset
from openslide import OpenSlide
from fastcore.foundation import L
from fastcore.xtras import is_listy

# Cell
class TestDataset(Dataset):
    def __init__(self, items, **kwargs):
        self.items = items.map(str)
        self.loader = ImageLoader(**kwargs)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        item = self.items[idx]
        img = self.loader(item)
        return np_to_tensor(img, "image")

# Cell
class TensorDataset(Dataset):
    """"""

    def __init__(
        self,
        ds: Dataset,
        tfms: Optional[Sequence[BasicTransform]] = None,
        tfm_y: bool = True,
    ):
        self._ds = ds
        self.tfms = ifnone(tfms, [])
        # for tfm_name in self._ds.item_loader.add_tfms:
        #    tfm = globals()[tfm_name]()
        #    self.tfms.append(tfm)
        self.tfm_y = tfm_y

    def __len__(self) -> int:
        return len(self._ds)

    def transform(self, x, y):
        if self.tfms != []:
            aug = Compose(self.tfms)
            augmented = aug(image=x, mask=y if self.tfm_y else None)
            x = augmented["image"]
            if self.tfm_y:
                y = augmented["mask"]
        return x, y

    def __getitem__(self, i: int) -> Tuple[torch.Tensor, torch.Tensor]:
        x, y = self._ds[i]
        if is_listy(x):
            x = list(x)
            for k in range(len(x)):
                x[k], y = self.transform(x[k], y)
                x[k] = np_to_tensor(
                    x[k],
                    type(self._ds.item_loader).__name__.lower().replace("loader", ""),
                )
        else:
            x, y = self.transform(x, y)
            x = np_to_tensor(
                x, type(self._ds.item_loader).__name__.lower().replace("loader", "")
            )
        y = np_to_tensor(
            y, type(self._ds.label_loader).__name__.lower().replace("loader", "")
        )
        return x, y

    def get_orig_tfmed(self, i: int) -> Tuple[torch.Tensor, torch.Tensor]:
        x, _ = self._ds[i]
        if self.tfms != []:
            aug = Compose(self.tfms)
            augmented = aug(image=x)
            x_tfmed = augmented["image"]
        else:
            x_tfmed = x
        return x, x_tfmed

    def __getattr__(self, name: str) -> Any:
        return getattr(self._ds, name)

    def __setattr__(self, name: str, value: Any):
        if name != "_ds" and hasattr(self._ds, name):
            setattr(self._ds, name, value)
        else:
            self.__dict__[name] = value

# Cell
@dataclass
class SplitDataset:
    """"""

    train: Dataset
    valid: Dataset
    test: Dataset = None

    def to_tensor(
        self,
        tfms: Optional[Sequence[BasicTransform]] = None,
        tfm_y: bool = True,
        test_tfms: Optional[Sequence[BasicTransform]] = None,
    ) -> TensorDataset:
        """
        Transforms all datasets into `TensorDataset` objects
        """
        tfms = ifnone(tfms, (None, None))
        self.train = self.train.to_tensor(tfms=tfms[0], tfm_y=tfm_y)
        self.valid = self.valid.to_tensor(tfms=tfms[1], tfm_y=tfm_y)
        if self.test is not None:
            self.test = self.test.to_tensor(tfms=test_tfms, tfm_y=tfm_y)
        return self

# Cell
class MyDataset(Dataset):
    """"""

    def __init__(
        self,
        items: Sequence[Any],
        labels: Sequence[Any],
        item_loader: ItemLoader,
        label_loader: ItemLoader,
        train_percent: float = 1
    ):
        super().__init__()
        self.items = np.array(items)
        self.labels = np.array(labels)
        self.select_items(train_percent)
        self.item_loader = item_loader
        self.label_loader = label_loader
        self.train_percent = train_percent

    def select_items(self, train_percent):
        nlim = int(train_percent*len(self.items))
        idxs = np.random.choice(np.arange(len(self.items)), size=nlim, replace=False)
        idxs.sort()
        self.items = self.items[idxs]
        self.labels = self.labels[idxs]

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, i: int) -> Tuple[Any, Any]:
        item, label = self.items[i], self.labels[i]
        x = self.item_loader(item)
        y = self.label_loader(label)
        return x, y

    @classmethod
    def from_folder(
        cls,
        folder: Path,
        label_func: Callable[[Path], Any],
        item_loader: ItemLoader,
        label_loader: ItemLoader,
        recurse: bool = True,
        extensions: Optional[Sequence[str]] = None,
        include: Optional[Sequence[str]] = None,
        exclude: Optional[Sequence[str]] = None,
        filterfunc: Optional[Callable[[Path], bool]] = None,
        train_percent: float = 1
    ):
        """
        Creates a `MyDataset` object by reading files from a folder. It uses `get_item` and therefore works the same.
        """
        folder = Path(folder)
        items = get_files(
            folder,
            recurse=recurse,
            extensions=extensions,
            folders=include
        )
        items = items.filter(filterfunc)
        labels = items.map(label_func)
        return cls(items, labels, item_loader, label_loader, train_percent=train_percent)

    def to_tensor(
        self, tfms: Optional[Sequence[BasicTransform]] = None, tfm_y: bool = True
    ) -> TensorDataset:
        """
        Creates a `TensorDataset` based on this dataset.
        """
        return TensorDataset(self, tfms=tfms, tfm_y=tfm_y)

    def split_by_list(
        self,
        train: Tuple[Sequence[Any], Sequence[Any]],
        valid: Tuple[Sequence[Any], Sequence[Any]],
        test: Optional[Tuple[Sequence[Any], Sequence[Any]]] = None,
    ) -> SplitDataset:
        """
        Creates a `SplitDataset` using `train`, `valid` and optionally `test` tuples. Each tuple contains 2 lists: one for items and one for labels.
        """
        return SplitDataset(
            self.__class__(train[0], train[1], self.item_loader, self.label_loader),
            self.__class__(valid[0], valid[1], self.item_loader, self.label_loader),
            None
            if test is None
            else self.__class__(test[0], test[1], self.item_loader, self.label_loader),
        )

    def split_by_folder(self) -> SplitDataset:
        """
        Creates a `SplitDataset` by looking for `ŧrain`, `valid` and `test` in item paths and splitting the dataset accordingly.
        """
        train = ([], [])
        valid = ([], [])
        test = ([], [])
        for item, label in zip(self.items, self.labels):
            if "train" in item.parts:
                train[0].append(item)
                train[1].append(label)
            elif "valid" in item.parts:
                valid[0].append(item)
                valid[1].append(label)
            elif "test" in item.parts:
                test[0].append(item)
                test[1].append(label)
        if test[0] == []:
            test = None
        return self.split_by_list(train, valid, test)

    def split_by_csv(
        self,
        csv: Union[Path, str],
        split_column: str = "split",
        id_column: str = "scan",
        get_id: Optional[Callable[[Any], Any]] = None,
    ) -> SplitDataset:
        """
        Creates a `SplitDataset` by using a csv that contains an `id_column` column for identifying items
        and a `split_column` column that contains either `'train'`, `'valid'` or `'test'`. `get_id` is the
        function used to extract the item's id from the item itself. By default it considers that `item` is a
        `Path` object and takes the parent folder's name as id.
        """
        get_id = ifnone(get_id, lambda x: x.parent.name)
        df = pd.read_csv(csv, header="infer")
        train = ([], [])
        valid = ([], [])
        test = ([], [])
        train_ids = df.loc[df[split_column] == "train", id_column]
        valid_ids = df.loc[df[split_column] == "valid", id_column]
        test_ids = df.loc[df[split_column] == "test", id_column]
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

# Cell
class ClassDataset(MyDataset):
    def __init__(self, *args, n_classes: int = 2, **kwargs):
        super().__init__(*args, **kwargs)
        self.n_classes = n_classes

# Cell
class ImageClassifDataset(ClassDataset):
    def show(
        self,
        k: int,
        ax: Axes = None,
        figsize: Tuple[int, int] = (3, 3),
        hide_axis: bool = True,
        cmap: str = "viridis",
        **kwargs
    ):
        """
        Shows the `k`th image from the dataset with the corresponding label.
        """
        x, y = self[k]
        y = self.label_loader.classes[y]
        ax = show_img(
            x,
            ax=ax,
            hide_axis=hide_axis,
            cmap=cmap,
            figsize=figsize,
            title=str(y),
            **kwargs
        )

    def show_rand(
        self,
        ax: Axes = None,
        figsize: Tuple[int, int] = (3, 3),
        hide_axis: bool = True,
        cmap: str = "viridis",
        **kwargs
    ):
        """
        Shows a random image from the dataset with the corresponding label.
        """
        k = random.randint(0, len(self) - 1)
        self.show(k, ax=ax, figsize=figsize, hide_axis=hide_axis, cmap=cmap, **kwargs)

    @classmethod
    def from_folder(
        cls,
        folder: Union[str, Path],
        label_func: Callable[[Path], Any],
        n_classes: Optional[int] = None,
        classes: Optional[Sequence[Any]] = None,
        recurse: bool = True,
        extensions: Optional[Sequence[str]] = None,
        include: Optional[Sequence[str]] = None,
        exclude: Optional[Sequence[str]] = None,
        filterfunc: Optional[Callable[[Path], bool]] = None,
        train_percent: float = 1,
        **kwargs
    ):
        """
        Overwrites `MyDataset.from_folder`. Works basically the same but you don't need to pass loaders, but instead `n_classes`
        or `classes` arguments. Loaders are automatically created using these.
        """
        items = get_files(
            folder,
            recurse=recurse,
            extensions=extensions,
            folders=include,
        )
        items = items.filter(filterfunc)
        labels = items.map(label_func)
        return cls(
            items,
            labels,
            ImageLoader(**kwargs),
            CategoryLoader(n_classes, classes),
            n_classes=ifnone(n_classes, len(classes)),
            train_percent=train_percent
        )

# Cell
class ImageSegmentDataset(ClassDataset):
    def show(
        self,
        k: int,
        ax: Axes = None,
        figsize: Tuple[int, int] = (3, 3),
        title: Optional[str] = None,
        hide_axis: bool = True,
        cmap: str = "tab20",
        **kwargs
    ):
        """
        Shows the `k`th image from the dataset with the corresponding mask above it.
        """
        x, y = self[k]
        ax = show_img(
            x, ax=ax, hide_axis=hide_axis, cmap=cmap, figsize=figsize, **kwargs
        )
        ax = show_img(
            y,
            ax=ax,
            hide_axis=hide_axis,
            cmap=cmap,
            figsize=figsize,
            interpolation="nearest",
            alpha=alpha,
            vmin=0,
            title=title,
            **kwargs
        )

    def show_rand(
        self,
        ax: Axes = None,
        figsize: Tuple[int, int] = (3, 3),
        hide_axis: bool = True,
        cmap: str = "tab20",
        **kwargs
    ):
        """
        Shows a random image from the dataset withthe corresponding mask above it.
        """
        k = random.randint(0, len(self) - 1)
        self.show(k, ax=ax, figsize=figsize, hide_axis=hide_axis, cmap=cmap, **kwargs)

    @classmethod
    def from_folder(
        cls,
        folder: Union[Path, str],
        label_func: Callable[[Path], Path],
        n_classes: Optional[int] = None,
        classes: Optional[Any] = None,
        recurse: bool = True,
        extensions: Optional[Sequence[str]] = None,
        include: Optional[Sequence[str]] = None,
        exclude: Optional[Sequence[str]] = None,
        filterfunc: Optional[Callable[[Path], bool]] = None,
        train_percent: float = 1
    ):
        """
        Same as `ImageClassifDataset.from_folder`.
        """
        items = get_items(
            folder,
            recurse=recurse,
            extensions=extensions,
            folders=include,
        )
        items = items.filter(filterfunc)
        labels = items.map(label_func)
        return cls(
            items,
            labels,
            ImageLoader(),
            MaskLoader(),
            n_classes=ifnone(n_classes, len(classes)),
            train_percent=train_percent
        )

# Cell
class NormDataset(MyDataset):
    def show(
        self,
        k: int,
        axs: Axes = None,
        figsize: Tuple[int, int] = (5, 5),
        title: Optional[str] = None,
        hide_axis: bool = True,
        cmap: str = "viridis",
        **kwargs
    ):
        """
        Shows the `k`th image from the dataset as grayscale and colored.
        """
        x, y = self[k]
        axs = ifnone(axs, plt.subplots(1, 2, figsize=figsize)[1])
        ax = show_img(
            x, ax=axs[0], hide_axis=hide_axis, cmap=cmap, figsize=figsize, **kwargs
        )
        ax = show_img(
            y, ax=axs[1], hide_axis=hide_axis, cmap=cmap, figsize=figsize, **kwargs
        )

    def __getitem__(self, i: int) -> Tuple[Any, Any]:
        item = self.items[i]
        x = self.item_loader(item)
        y = x.copy()
        return x, y

    def show_rand(
        self,
        axs: Axes = None,
        figsize: Tuple[int, int] = (5, 5),
        hide_axis: bool = True,
        cmap: str = "viridis",
        **kwargs
    ):
        """
        Shows a random image from the dataset as grayscale and colored.
        """
        k = random.randint(0, len(self) - 1)
        self.show(k, axs=axs, figsize=figsize, hide_axis=hide_axis, cmap=cmap, **kwargs)

    @classmethod
    def from_folder(
        cls,
        folder: Union[Path, str],
        recurse: bool = True,
        extensions: Optional[Sequence[str]] = None,
        include: Optional[Sequence[str]] = None,
        exclude: Optional[Sequence[str]] = None,
        filterfunc: Optional[Callable[[Path], bool]] = None,
        train_percent: float = 1,
        **kwargs
    ):
        """
        Overwrites `MyDataset.from_folder` so that it doesn't need the loaders or a `label_func`.
        """
        items = get_files(
            folder,
            recurse=recurse,
            extensions=extensions,
            folders=include,
        )
        items = items.filter(filterfunc)
        labels = items.copy()
        return cls(items, labels, ImageLoader(**kwargs), ImageLoader(), train_percent=train_percent)

# Cell
class MILDataset(ClassDataset):
    def __init__(
        self,
        items: Sequence[str],
        labels: Sequence[str],
        slides: Sequence[OpenSlide],
        slide_idxs: Sequence[int],
        slide_labels: Sequence[str],
        classes: Sequence[str],
        train_percent: float = 1,
        **kwargs,
    ):
        self.classes = ifnone(classes, [0, 1])
        assert len(self.classes) == 2, "Multiple Instance learning only works with 2 classes"
        self.slides = np.array(slides)
        self.slide_labels = np.array(slide_labels)
        self.slide_idxs = np.array(slide_idxs)
        super().__init__(
            items,
            labels,
            SlideLoader(**kwargs),
            CategoryLoader(classes=self.classes),
            n_classes=2,
            train_percent=train_percent,
        )

    def select_items(self, train_percent):
        nlim = max(1, int(train_percent * len(self.slides)))
        idxs = np.random.choice(np.arange(len(self.slides)), size=nlim, replace=False)
        idxs.sort()
        self.slides = self.slides[idxs]
        self.slide_labels = self.slide_labels[idxs]
        idxs = np.argwhere(np.vectorize(lambda x: x in idxs)(self.slide_idxs)).squeeze(1)
        self.items = self.items[idxs]
        self.labels = self.labels[idxs]
        self.slide_idxs = self.slide_idxs[idxs]
        for k, idx in enumerate(np.unique(self.slide_idxs)):
            self.slide_idxs[self.slide_idxs == idx] = k

    def __getitem__(self, i: int) -> Tuple[Any, Any]:
        item, label = self.items[i], self.labels[i]
        slide = self.slides[self.slide_idxs[i]]
        x = self.item_loader(item, slide)
        y = self.label_loader(label)
        return x, y

    @classmethod
    def from_folder(
        cls,
        folder: Union[str, Path],
        label_func: Callable[[Path], str],
        coord_csv: Union[str, Path],
        classes: Optional[Sequence[str]] = None,
        recurse: bool = True,
        extensions: Optional[Sequence[str]] = None,
        include: Optional[Sequence[str]] = None,
        filterfunc: Optional[Callable[[Path], bool]] = None,
        train_percent: float = 1,
        **kwargs,
    ):
        """
        Overwrites `MyDataset.from_folder`. Works basically the same but you don't need to pass loaders, but instead `n_classes`
        or `classes` arguments. Loaders are automatically created using these.
        """
        files = get_files(
            folder,
            recurse=recurse,
            extensions=extensions,
            folders=include,
        )
        files = files.filter(filterfunc)
        slide_labels = files.map(label_func)
        slides = files.map(lambda x: OpenSlide(str(x)))
        coord_df = pd.read_csv(coord_csv)
        labels = []
        items = []
        slide_idxs = []
        for k, (file, label) in enumerate(zip(files, slide_labels)):
            slide_coords = coord_df.loc[coord_df["Slidename"] == file.stem].values[
                :, 1:3
            ]
            n_coords = len(slide_coords)
            labels.extend([label] * n_coords)
            slide_idxs.extend([k] * n_coords)
            for coord in slide_coords:
                x, y = coord
                items.append(f"{file.stem}__{x}__{y}")
        return cls(
            L(items),
            L(labels),
            L(slides),
            L(slide_idxs),
            L(slide_labels),
            classes,
            train_percent=train_percent,
            **kwargs,
        )

    def split_by_list(
        self,
        train: Tuple[
            Sequence[str],
            Sequence[str],
            Sequence[OpenSlide],
            Sequence[int],
            Sequence[str],
        ],
        valid: Tuple[
            Sequence[str],
            Sequence[str],
            Sequence[OpenSlide],
            Sequence[int],
            Sequence[str],
        ],
        test: Tuple[
            Sequence[str],
            Sequence[str],
            Sequence[OpenSlide],
            Sequence[int],
            Sequence[str],
        ],
    ) -> SplitDataset:
        """
        Creates a `SplitDataset` using `train`, `valid` and optionally `test` tuples. Each tuple contains 2 lists: one for items and one for labels.
        """
        return SplitDataset(
            self.__class__(
                *train,
                self.classes,
            ),
            self.__class__(
                *valid,
                self.classes,
            ),
            self.__class__(
                *test,
                self.classes,
            ),
        )

    def split_by_csv(
        self,
        csv: Union[Path, str],
        split_column: str = "split",
        id_column: str = "scan",
    ) -> SplitDataset:
        """
        Creates a `SplitDataset` by using a csv that contains an `id_column` column for identifying items
        and a `split_column` column that contains either `'train'`, `'valid'` or `'test'`. `get_id` is the
        function used to extract the item's id from the item itself. By default it considers that `item` is a
        `Path` object and takes the parent folder's name as id.
        """

        def get_id(item):
            return item.split("__")[0]

        df = pd.read_csv(csv, header="infer")
        train = (L(), L(), L(), L(), L())
        valid = (L(), L(), L(), L(), L())
        test = (L(), L(), L(), L(), L())
        train_ids = df.loc[df[split_column] == "train", id_column]
        valid_ids = df.loc[df[split_column] == "valid", id_column]
        k_train = -1
        k_valid = -1
        train_idxs = []
        val_idxs = []
        for item, label, slide_idx in zip(self.items, self.labels, self.slide_idxs):
            item_id = get_id(item)
            if item_id in train_ids.values:
                train[0].append(item)
                train[1].append(label)
                test[0].append(item)
                test[1].append(label)
                if slide_idx not in train_idxs:
                    train_idxs.append(slide_idx)
                    train[2].append(self.slides[slide_idx])
                    train[4].append(self.slide_labels[slide_idx])
                    test[2].append(self.slides[slide_idx])
                    test[4].append(self.slide_labels[slide_idx])
                    k_train += 1
                train[3].append(k_train)
                test[3].append(k_train)
            elif item_id in valid_ids.values:
                valid[0].append(item)
                valid[1].append(label)
                if slide_idx not in val_idxs:
                    val_idxs.append(slide_idx)
                    valid[2].append(self.slides[slide_idx])
                    valid[4].append(self.slide_labels[slide_idx])
                    k_valid += 1
                valid[3].append(k_valid)
        return self.split_by_list(train, valid, test)

# Cell
class RNNSlideDataset(ClassDataset):
    def __init__(
        self,
        items: Sequence[str],
        labels: Sequence[str],
        slides: Sequence[OpenSlide],
        classes: Sequence[str],
        patches_per_slide: int = 10,
        train_percent: float = 1,
        **kwargs,
    ):
        self.classes = classes
        self.slides = np.array(slides)
        self.patches_per_slide = patches_per_slide
        super().__init__(
            items,
            labels,
            SlideLoader(**kwargs),
            CategoryLoader(classes=classes),
            n_classes=len(classes),
            train_percent=train_percent,
        )

    def select_items(self, train_percent):
        nlim = max(1, int(train_percent * len(self.slides)))
        idxs = np.random.choice(np.arange(len(self.slides)), size=nlim, replace=False)
        idxs.sort()
        self.slides = self.slides[idxs]
        self.items = self.items[idxs]
        self.labels = self.labels[idxs]

    def __getitem__(self, i: int) -> Tuple[Any, Any]:
        item, label, slide = self.items[i], self.labels[i], self.slides[i]
        x = []
        slidename, *coords = item.split("__")
        for coord in coords[: self.patches_per_slide]:
            item = "__".join([slidename] + coord.split("_"))
            x.append(self.item_loader(item, slide))
        y = self.label_loader(label)
        return x, y

    @classmethod
    def from_folder(
        cls,
        folder: Union[str, Path],
        label_func: Callable[[Path], str],
        coord_csv: Union[str, Path],
        classes: Optional[Sequence[str]] = None,
        recurse: bool = True,
        extensions: Optional[Sequence[str]] = None,
        include: Optional[Sequence[str]] = None,
        filterfunc: Optional[Callable[[Path], bool]] = None,
        train_percent: float = 1,
        patches_per_slide=10,
        **kwargs,
    ):
        """
        Overwrites `MyDataset.from_folder`. Works basically the same but you don't need to pass loaders, but instead `n_classes`
        or `classes` arguments. Loaders are automatically created using these.
        """
        files = get_files(
            folder,
            recurse=recurse,
            extensions=extensions,
            folders=include,
        )
        files = files.filter(filterfunc)
        labels = files.map(label_func)
        slides = files.map(lambda x: OpenSlide(str(x)))
        coord_df = pd.read_csv(coord_csv)
        items = []
        for file in files:
            slide_coords = coord_df.loc[coord_df["Slidename"] == file.stem].values[
                :, 1:
            ]
            item = file.stem
            for coord in slide_coords[:patches_per_slide]:
                x, y = coord
                item += f"__{x}_{y}"
            items.append(item)
        return cls(
            L(items),
            L(labels),
            L(slides),
            classes,
            train_percent=train_percent,
            patches_per_slide=patches_per_slide,
            **kwargs,
        )

    def split_by_list(
        self,
        train: Tuple[Sequence[str], Sequence[str], Sequence[OpenSlide]],
        valid: Tuple[Sequence[str], Sequence[str], Sequence[OpenSlide]],
        test: Optional[Tuple[Sequence[str], Sequence[str], Sequence[OpenSlide]]] = None,
    ) -> SplitDataset:
        """
        Creates a `SplitDataset` using `train`, `valid` and optionally `test` tuples. Each tuple contains 2 lists: one for items and one for labels.
        """
        return SplitDataset(
            self.__class__(
                *train, self.classes, patches_per_slide=self.patches_per_slide
            ),
            self.__class__(
                *valid, self.classes, patches_per_slide=self.patches_per_slide
            ),
            None
            if test is None
            else self.__class__(
                *test, self.classes, patches_per_slide=self.patches_per_slide
            ),
        )

    def split_by_csv(
        self,
        csv: Union[Path, str],
        split_column: str = "split",
        id_column: str = "scan",
    ) -> SplitDataset:
        """
        Creates a `SplitDataset` by using a csv that contains an `id_column` column for identifying items
        and a `split_column` column that contains either `'train'`, `'valid'` or `'test'`. `get_id` is the
        function used to extract the item's id from the item itself. By default it considers that `item` is a
        `Path` object and takes the parent folder's name as id.
        """

        def get_id(item):
            return item.split("__")[0]

        df = pd.read_csv(csv, header="infer")
        train = (L(), L(), L())
        valid = (L(), L(), L())
        test = (L(), L(), L())
        train_ids = df.loc[df[split_column] == "train", id_column]
        valid_ids = df.loc[df[split_column] == "valid", id_column]
        test_ids = df.loc[df[split_column] == "test", id_column]
        for item, label, slide in zip(self.items, self.labels, self.slides):
            item_id = get_id(item)
            if item_id in train_ids.values:
                train[0].append(item)
                train[1].append(label)
                train[2].append(slide)
            elif item_id in valid_ids.values:
                valid[0].append(item)
                valid[1].append(label)
                valid[2].append(slide)
            elif item_id in test_ids.values:
                test[0].append(item)
                test[1].append(label)
                test[2].append(slide)
        if test[0] == []:
            test = None
        return self.split_by_list(train, valid, test)