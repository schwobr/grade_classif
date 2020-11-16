#AUTOGENERATED! DO NOT EDIT! File to edit: dev/11_data.loaders.ipynb (unless otherwise specified).

__all__ = ['ItemLoader', 'ImageLoader', 'MaskLoader', 'CategoryLoader']

#Cell
from ..imports import *
from skimage.color import rgb2hed

#Cell
class ItemLoader:
    def __call__(self, item: Any):
        raise NotImplementedError

#Cell
class ImageLoader(ItemLoader):
    def __init__(self, div: bool = True):
        # self.open_mode = open_mode
        self.div = div
        # self.add_tfms = ['RGB2'+self.open_mode] if self.open_mode in ['HEG', 'H', 'E'] else []

    def __call__(self, item: Path) -> NDArray[(Any, Any, 3), Number]:
        img = cv2.imread(str(item), cv2.IMREAD_UNCHANGED)
        if img.shape[-1] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if self.div:
            img = img.astype(np.float32) / 255
        return img

#Cell
class MaskLoader(ImageLoader):
    def __init__(self):
        super().__init__(div=False)

#Cell
class CategoryLoader(ItemLoader):
    def __init__(
        self, n_classes: Optional[int] = None, classes: Optional[List[Any]] = None
    ):
        if n_classes is not None:
            self.n_classes = n_classes
            if classes is None:
                self.classes = list(range(n_classes))
            else:
                self.classes = classes
        else:
            assert (
                classes is not None
            ), "you must either specify a list of classes or a number of classes"
            self.classes = classes
            self.n_classes = len(classes)

    def __call__(self, item: Any) -> int:
        return self.classes.index(item)