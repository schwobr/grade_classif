#AUTOGENERATED! DO NOT EDIT! File to edit: dev/04_data_loaders.ipynb (unless otherwise specified).

__all__ = ['ImageLoader', 'MaskLoader', 'CategoryLoader']

#Cell
import cv2

#Cell
class ImageLoader:
    def __init__(self, open_mode='RGB', div=True):
        self.open_mode = open_mode
        self.div = div

    def __call__(self, item):
        mode = cv2.IMREAD_COLOR if self.open_mode == 'RGB' else cv2.IMREAD_GRAYSCALE
        img = cv2.imread(str(item), mode)
        if self.open_mode is not 'G':
            cvt_mode = cv2.COLOR_BGR2RGB if self.open_mode == 'RGB' else cv2.COLOR_GRAY2RGB
            img = cv2.cvtColor(img, cvt_mode)
        if self.div:
            img = img.astype(np.float32)/255
        return img

#Cell
class MaskLoader(ImageLoader):
    def __init__(self):
        super().__init__(open_mode='G', div=False)

#Cell
class CategoryLoader:
    def __init__(self, n_classes=None, classes=None):
        if n_classes is not None:
            self.n_classes = n_classes
            if classes is None:
                self.classes = list(range(n_classes))
            else:
                self.classes = classes
        else:
            assert classes is not None, "you must either specify a list of classes or a number of classes"
            self.classes = classes
            self.n_classes = len(classes)

    def __call__(self, item):
        return self.classes.index(item)