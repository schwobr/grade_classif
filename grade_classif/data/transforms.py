# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/14_data.transforms.ipynb (unless otherwise specified).

__all__ = ['DeterministicHSV', 'DeterministicBrightnessContrast', 'DeterministicGamma', 'DeterministicRGBShift',
           'RGB2H', 'RGB2E', 'RGB2HEG', 'RandomCropResizeStack', 'CenterCropResizeStack', 'StainAugmentor',
           'get_transforms1', 'get_transforms2', 'get_transforms3', 'get_transforms4', 'get_transforms5',
           'get_transforms10']

# Cell
from albumentations import (RandomRotate90,
                            Flip,
                            Transpose,
                            GridDistortion,
                            RandomCrop,
                            GaussianBlur,
                            RandomGamma,
                            RandomBrightnessContrast,
                            HueSaturationValue,
                            RGBShift,
                            CenterCrop,
                            ImageOnlyTransform,
                            DualTransform,
                            BasicTransform)
import albumentations.augmentations.functional as F
from ..imports import *
from ..core import ifnone
from math import floor
from skimage.color import rgb2hed
import random
from staintools.stain_extraction.vahadane_stain_extractor import VahadaneStainExtractor
from staintools.miscellaneous.get_concentrations import get_concentrations
from staintools.miscellaneous.optical_density_conversion import convert_RGB_to_OD

# Cell
def _shift_hsv_non_uint8(
    img: NDArray[(Any, Any, 3), Number],
    hue_shift: int,
    sat_shift: float,
    val_shift: float,
) -> NDArray[(Any, Any, 3), Number]:
    dtype = img.dtype
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hue, sat, val = cv2.split(img)
    hue = cv2.add(hue, hue_shift)
    hue = np.where(hue < 0, hue + 360, hue)
    hue = np.where(hue > 360, hue - 360, hue)
    hue = hue.astype(dtype)
    sat = F.clip(
        sat + sat_shift * (sat > 0.1), dtype, 255 if dtype == np.uint8 else 1.0
    )
    val = F.clip(
        val + val_shift * (sat > 0.1), dtype, 255 if dtype == np.uint8 else 1.0
    )
    img = cv2.merge((hue, sat, val)).astype(dtype)
    img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    return img


F._shift_hsv_non_uint8 = _shift_hsv_non_uint8

# Cell
def _mod(x: Number, y: Number) -> Number:
    x -= floor(x / y) * y
    return x

# Cell
def _get_params(tfm: BasicTransform) -> Dict[str, Number]:
    params = {}
    for k, v in tfm.base_values.items():
        v_min, v_max = tfm.max_values[k]
        if v_min == v_max:
            params[k] = v_min
        else:
            p = v + tfm.n * tfm.mult
            p = _mod(p - v_min, v_max - v_min) + v_min
            params[k] = p
    tfm.n += 1
    tfm.n %= tfm.num_els
    return params

# Cell
def _init_attrs(tfm: BasicTransform, num_els: int = 1):
    tfm.always_apply = True
    tfm.num_els = num_els
    tfm.p = 1
    tfm.n = 0
    tfm.mult = 83
    tfm.base_values = {
        x: (x_lim[1] - x_lim[0]) / 7 for x, x_lim in tfm.max_values.items()
    }

# Cell
class DeterministicHSV(HueSaturationValue):
    def __init__(self, num_els: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.max_values = {
            "hue_shift": self.hue_shift_limit,
            "sat_shift": self.sat_shift_limit,
            "val_shift": self.val_shift_limit,
        }
        _init_attrs(self, num_els)

    def get_params(self) -> Dict[str, Number]:
        return _get_params(self)

# Cell
class DeterministicBrightnessContrast(RandomBrightnessContrast):
    def __init__(self, num_els: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.max_values = {
            "alpha": tuple(x + 1 for x in self.contrast_limit),
            "beta": self.brightness_limit,
        }
        _init_attrs(self, num_els)

    def get_params(self) -> Dict[str, Number]:
        return _get_params(self)

# Cell
class DeterministicGamma(RandomGamma):
    def __init__(self, num_els: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.max_values = {"gamma": tuple(x / 100 for x in self.gamma_limit)}
        _init_attrs(self, num_els)

    def get_params(self) -> Dict[str, Number]:
        return _get_params(self)

# Cell
class DeterministicRGBShift(RGBShift):
    def __init__(self, num_els: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.max_values = {
            "r_shift": self.r_shift_limit,
            "g_shift": self.g_shift_limit,
            "b_shift": self.b_shift_limit,
        }
        _init_attrs(self, num_els)

    def get_params(self) -> Dict[str, Number]:
        return _get_params(self)

# Cell
class RGB2H(ImageOnlyTransform):
    def __init__(self, always_apply: bool = True, p: float = 1):
        super(RGB2H, self).__init__(always_apply, p)

    def apply(
        self, image: NDArray[(Any, Any, 3), Number], **params
    ) -> NDArray[(Any, Any, 3), Number]:
        img = rgb2hed(image)[..., 0].astype(np.float32)
        img = (img + 0.7) / 0.46
        return np.stack((img, img, img), axis=-1)

    def get_transform_init_args_names(self) -> List:
        return []

# Cell
class RGB2E(ImageOnlyTransform):
    def __init__(self, always_apply: bool = True, p: float = 1):
        super(RGB2E, self).__init__(always_apply, p)

    def apply(
        self, image: NDArray[(Any, Any, 3), Number], **params
    ) -> NDArray[(Any, Any, 3), Number]:
        img = rgb2hed(image)[..., 1].astype(np.float32)
        img = (img + 0.1) / 0.47
        return np.stack((img, img, img), axis=-1)

    def get_transform_init_args_names(self) -> List:
        return []

# Cell
class RGB2HEG(ImageOnlyTransform):
    def __init__(self, always_apply: bool = True, p: float = 1):
        super(RGB2HEG, self).__init__(always_apply, p)

    def apply(
        self, image: NDArray[(Any, Any, 3), Number], **params
    ) -> NDArray[(Any, Any, 3), Number]:
        tfmed = rgb2hed(image).astype(np.float32)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return np.concatenate((tfmed[..., :2], gray[..., None]), axis=-1)

    def get_transform_init_args_names(self) -> List:
        return []

# Cell
class RandomCropResizeStack(DualTransform):
    def __init__(
        self, size: int, n_inputs: int = 3, always_apply: bool = True, p: float = 1
    ):
        super().__init__(always_apply, p)
        self.size = size
        self.n_inputs = n_inputs

    def apply(self, img, **params):
        imgs = []
        max_size = int(self.size * 2 ** (self.n_inputs - 1))
        if img.shape[0] < max_size:
            img = F.resize(img, max_size, max_size)
        for k in range(self.n_inputs):
            h, w = img.shape[:2]
            if k > 0:
                img = F.resize(img, h // 2, w // 2)
            imgs.append(
                F.random_crop(
                    img,
                    self.size,
                    self.size,
                    params[f"h_start_{k}"],
                    params[f"w_start_{k}"]
                )
            )
        return np.concatenate(imgs, axis=-1)

    def get_params(self):
        params = {}
        for k in range(self.n_inputs):
            params[f"h_start_{k}"] = random.random()
            params[f"w_start_{k}"] = random.random()
        return params

    def get_transform_init_args_names(self):
        return ("size", "n_inputs")

# Cell
class CenterCropResizeStack(DualTransform):
    def __init__(
        self, size: int, n_inputs: int = 3, always_apply: bool = True, p: float = 1
    ):
        super().__init__(always_apply, p)
        self.size = size
        self.n_inputs = n_inputs

    def apply(self, img, **params):
        imgs = []
        max_size = int(self.size * 2 ** (self.n_inputs - 1))
        if img.shape[0] < max_size:
            img = F.resize(img, max_size, max_size)
        for k in range(self.n_inputs):
            h, w = img.shape[:2]
            if k > 0:
                img = F.resize(img, h // 2, w // 2)
            imgs.append(
                F.center_crop(
                    img,
                    self.size,
                    self.size
                )
            )
        return np.concatenate(imgs, axis=-1)

    def get_transform_init_args_names(self):
        return ("size", "n_inputs")

# Cell
class StainAugmentor(ImageOnlyTransform):
    def __init__(
        self,
        alpha_range: float = 0.4,
        beta_range: float = 0.4,
        alpha_stain_range: float = 0.3,
        beta_stain_range: float = 0.2,
        he_ratio: float = 0.3,
        always_apply: bool = True,
        p: float = 1,
    ):
        super(StainAugmentor, self).__init__(always_apply, p)
        self.alpha_range = alpha_range
        self.beta_range = beta_range
        self.alpha_stain_range = alpha_stain_range
        self.beta_stain_range = beta_stain_range
        self.he_ratio = he_ratio
        self.stain_matrix = np.array(
            [[0.56371366, 0.77129725, 0.29551221], [0.1378605, 0.82185632, 0.55276276]]
        )

    def get_params(self):
        return {
            "alpha": np.random.uniform(
                1 - self.alpha_range, 1 + self.alpha_range, size=2
            ),
            "beta": np.random.uniform(-self.beta_range, self.beta_range, size=2),
            "alpha_stain": np.stack(
                (
                    np.random.uniform(
                        1 - self.alpha_stain_range * self.he_ratio,
                        1 + self.alpha_stain_range * self.he_ratio,
                        size=3,
                    ),
                    np.random.uniform(
                        1 - self.alpha_stain_range,
                        1 + self.alpha_stain_range,
                        size=3,
                    ),
                ),
            ),
            "beta_stain": np.stack(
                (
                    np.random.uniform(
                        -self.beta_stain_range * self.he_ratio,
                        self.beta_stain_range * self.he_ratio,
                        size=3,
                    ),
                    np.random.uniform(
                        -self.beta_stain_range, self.beta_stain_range, size=3
                    ),
                ),
            ),
        }

    def initialize(self, alpha, beta, shape=2):
        alpha = ifnone(alpha, np.ones(shape))
        beta = ifnone(beta, np.zeros(shape))
        return alpha, beta

    def apply(
        self,
        image: NDArray[(Any, Any, 3), Number],
        alpha: Optional[NDArray[(2,), float]] = None,
        beta: Optional[NDArray[(2,), float]] = None,
        alpha_stain: Optional[NDArray[(2, 3), float]] = None,
        beta_stain: Optional[NDArray[(2, 3), float]] = None,
        **params
    ) -> NDArray[(Any, Any, 3), Number]:
        alpha, beta = self.initialize(alpha, beta, shape=2)
        alpha_stain, beta_stain = self.initialize(alpha_stain, beta_stain, shape=(2, 3))
        if not image.dtype == np.uint8:
            image = (image * 255).astype(np.uint8)
        # stain_matrix = VahadaneStainExtractor.get_stain_matrix(image)
        HE = get_concentrations(image, self.stain_matrix)
        #HE = convert_RGB_to_OD(image).reshape((-1, 3)) @ np.linalg.pinv(self.stain_matrix)
        stain_matrix = self.stain_matrix * alpha_stain + beta_stain
        stain_matrix = np.clip(stain_matrix, 0, 1)
        HE = np.where(HE > 0.2, HE * alpha[None] + beta[None], HE)
        out = np.exp(-np.dot(HE, stain_matrix)).reshape(image.shape)
        out = np.clip(out, 0, 1)
        return out.astype(np.float32)

    def get_transform_init_args_names(self) -> List:
        return ("alpha_range", "beta_range", "alpha_stain_range", "beta_stain_range", "he_ratio")

# Cell
def get_transforms1(
    size: int, num_els: int = 1
) -> Tuple[List[BasicTransform], List[BasicTransform]]:
    tfms = [
        RandomCrop(size, size),
        RandomRotate90(),
        Flip(),
        Transpose(),
        GridDistortion(distort_limit=0.05, p=0.2),
        RandomGamma(p=0.2),
        GaussianBlur(blur_limit=3, p=0.2),
    ]
    val_tfms = [CenterCrop(size, size)]
    return tfms, val_tfms

# Cell
def get_transforms2(
    size: int, num_els: int = 1
) -> Tuple[List[BasicTransform], List[BasicTransform]]:
    tfms = [
        RandomCrop(size, size),
        RandomRotate90(),
        Flip(),
        Transpose(),
        GridDistortion(distort_limit=0.05, p=0.2),
        RandomGamma(p=0.2),
        GaussianBlur(blur_limit=3, p=0.2),
        RGBShift(0.15, 0.15, 0.15),
    ]
    val_tfms = [CenterCrop(size, size)]
    return tfms, val_tfms

# Cell
def get_transforms3(
    size: int, num_els: int = 1
) -> Tuple[List[BasicTransform], List[BasicTransform]]:
    tfms = [
        RandomCrop(size, size),
        RandomRotate90(),
        Flip(),
        Transpose(),
        GridDistortion(distort_limit=0.05, p=0.2),
        RandomBrightnessContrast(p=0.7),
        GaussianBlur(blur_limit=3, p=0.2),
        RGBShift(0.2, 0.2, 0.2, p=0.8),
    ]
    val_tfms = [
        CenterCrop(size, size),
        DeterministicBrightnessContrast(num_els=num_els),
        DeterministicRGBShift(
            num_els=num_els, r_shift_limit=0.2, g_shift_limit=0.2, b_shift_limit=0.2
        ),
    ]
    return tfms, val_tfms

# Cell
def get_transforms4(
    size: int, num_els: int = 1
) -> Tuple[List[BasicTransform], List[BasicTransform]]:
    tfms = [
        RandomCrop(size, size),
        StainAugmentor(),
        RandomRotate90(),
        Flip(),
        Transpose(),
        RandomGamma(),
    ]
    val_tfms = [
        CenterCrop(size, size)
    ]
    return tfms, val_tfms

# Cell
def get_transforms5(
    size: int, num_els: int = 1
) -> Tuple[List[BasicTransform], List[BasicTransform]]:
    tfms = [
        RandomCrop(size, size),
        StainAugmentor(he_ratio=0.5),
        RandomRotate90(),
        Flip(),
        Transpose(),
        RandomGamma(),
    ]
    val_tfms = [
        CenterCrop(size, size),
        StainAugmentor(he_ratio=0.5),
    ]
    return tfms, val_tfms

# Cell
def get_transforms10(
    size: int, n_inputs : int = 3
) -> Tuple[List[BasicTransform], List[BasicTransform]]:
    tfms = [
        RandomRotate90(),
        Flip(),
        Transpose(),
        RandomGamma(),
        HueSaturationValue(20, 0.1, 0.1, p=1),
        RandomCropResizeStack(size, n_inputs=n_inputs)
    ]
    val_tfms = [
        CenterCropResizeStack(size, n_inputs=n_inputs)
    ]
    return tfms, val_tfms