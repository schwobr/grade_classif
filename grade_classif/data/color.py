# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/15_data.color.ipynb (unless otherwise specified).

__all__ = ['rgb_to_lab', 'rgb_to_hed', 'rgb_to_h', 'rgb_to_e', 'rgb_to_heg', 'ColorConverter']

# Cell
from ..imports import *
from scipy import linalg
from kornia.color import rgb_to_xyz, rgb_to_grayscale, rgb_to_hsv

# Cell
_xyz_ref_white = (.950456, 1., 1.088754)

# Cell
def rgb_to_lab(image: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    r"""Converts a RGB image to Luv.

    See :class:`~kornia.color.RgbToLuv` for details.

    Args:
        image (torch.Tensor): RGB image
        eps (float): for numerically stability when dividing. Default: 1e-8.

    Returns:
        torch.Tensor : Luv image
    """

    if not torch.is_tensor(image):
        raise TypeError("Input type is not a torch.Tensor. Got {}".format(type(image)))

    if len(image.shape) < 3 or image.shape[-3] != 3:
        raise ValueError(
            "Input size must have a shape of (*, 3, H, W). Got {}".format(image.shape)
        )

    image = image.float()

    # Convert from Linear RGB to sRGB
    r = image[..., 0, :, :]
    g = image[..., 1, :, :]
    b = image[..., 2, :, :]

    rs = torch.where(r > 0.04045, torch.pow(((r + 0.055) / 1.055), 2.4), r / 12.92)
    gs = torch.where(g > 0.04045, torch.pow(((g + 0.055) / 1.055), 2.4), g / 12.92)
    bs = torch.where(b > 0.04045, torch.pow(((b + 0.055) / 1.055), 2.4), b / 12.92)

    image_s = torch.stack((rs, gs, bs), dim=-3)

    xyz_im: torch.Tensor = rgb_to_xyz(image)

    x = xyz_im[..., 0, :, :]
    y = xyz_im[..., 1, :, :]
    z = xyz_im[..., 2, :, :]

    x = x / _xyz_ref_white[0]
    z = z / _xyz_ref_white[2]

    L = torch.where(
        torch.gt(y, 0.008856), 116.0 * torch.pow(y, 1.0 / 3.0) - 16.0, 903.3 * y
    )

    def _f(t):
        return torch.where(
            torch.gt(t, 0.008856), torch.pow(t, 1 / 3), 7.787 * t + 4 / 29
        )

    # Compute reference white point
    a = 500 * (_f(x) - _f(y))
    b = 200 * (_f(y) - _f(z))

    out = torch.stack((L, a, b), dim=-3)
    return out

# Cell
_rgb_from_hed = torch.tensor([[0.65, 0.70, 0.29],
                              [0.07, 0.99, 0.11],
                              [0.27, 0.57, 0.78]], dtype=torch.float32)
_hed_from_rgb = torch.inverse(_rgb_from_hed)

# Cell
def rgb_to_hed(image: torch.Tensor, conversion_matrix: torch.Tensor) -> torch.Tensor:
    if len(image.shape) == 4:
        perm1 = (0, 2, 3, 1)
        perm2 = (0, 3, 1, 2)
    else:
        perm1 = (1, 2, 0)
        perm2 = (2, 0, 1)
    image += 2
    stains = -(torch.log(image) / np.log(10)).permute(*perm1) @ conversion_matrix
    return stains.permute(*perm2)

# Cell
def rgb_to_h(image: torch.Tensor, conversion_matrix: torch.Tensor) -> torch.Tensor:
    if len(image.shape) == 4:
        h = rgb_to_hed(image, conversion_matrix)[:, 0]
        h = (h + 0.7) / 0.46
        return torch.stack((h, h, h), axis=1)
    else:
        h = rgb_to_hed(image, conversion_matrix)[0]
        h = (h + 0.7) / 0.46
        return torch.stack((h, h, h), axis=0)

# Cell
def rgb_to_e(image: torch.Tensor, conversion_matrix: torch.Tensor) -> torch.Tensor:
    if len(image.shape) == 4:
        e = rgb_to_hed(image, conversion_matrix)[:, 1]
        e = (e + 0.1) / 0.47
        return torch.stack((e, e, e), axis=1)
    else:
        e = rgb_to_hed(image, conversion_matrix)[1]
        e = (e + 0.1) / 0.47
        return torch.stack((e, e, e), axis=0)

# Cell
def rgb_to_heg(image: torch.Tensor, conversion_matrix: torch.Tensor) -> torch.Tensor:
    gray = rgb_to_grayscale(image)
    hed = rgb_to_hed(image, conversion_matrix)
    if len(image.shape) == 4:
        h, e = hed[:, 0], hed[:, 1]
        h = (h + 0.7) / 0.46
        e = (e + 0.1) / 0.47
        return torch.stack((h, e, gray.squeeze(1)), axis=1)
    else:
        h, e = hed[0], hed[1]
        h = (h + 0.7) / 0.46
        e = (e + 0.1) / 0.47
        return torch.stack((h, e, gray.squeeze(0)), axis=0)

# Cell
class ColorConverter(nn.Module):
    def __init__(self, open_mode="rgb"):
        super().__init__()
        self.open_mode = open_mode.lower()
        if self.open_mode in ("h", "e", "heg", "hed"):
            self.conversion_matrix = nn.Parameter(
                torch.inverse(_rgb_from_hed), requires_grad=False
            )
        else:
            self.conversion_matrix = None

    def forward(self, x):
        if self.open_mode != "rgb":
            open_func = globals()[f"rgb_to_{self.open_mode}"]
            if self.conversion_matrix is None:
                x = open_func(x)
            else:
                x = open_func(x, self.conversion_matrix)
        return x