# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/22_models.utils.ipynb (unless otherwise specified).

__all__ = ['named_leaf_modules', 'get_sizes', 'gaussian_mask', 'get_num_features']

# Cell
from ..core import ifnone
from .hooks import Hooks
from ..imports import *
import pytorch_lightning as pl
from pytorch_lightning.metrics import Metric
from pytorch_lightning.callbacks import Callback

# Cell
def named_leaf_modules(model, name=""):
    named_children = list(model.named_children())
    if named_children == []:
        model.name = name
        return [model]
    else:
        res = []
        for n, m in named_children:
            if not (isinstance(m, torch.jit.ScriptModule) or isinstance(m, Metric)):
                pref = name + "." if name != "" else ""
                res += named_leaf_modules(m, pref + n)
        return res

# Cell
def get_sizes(model, input_shape=(3, 224, 224), leaf_modules=None):
    leaf_modules = ifnone(leaf_modules, named_leaf_modules(model))

    class Count:
        def __init__(self):
            self.k = 0
    count = Count()
    def _hook(model, input, output):
        model.k = count.k
        count.k += 1
        return model, output.shape

    with Hooks(leaf_modules, _hook) as hooks:
        x = torch.rand(1, *input_shape)
        model.cpu().eval()(x)
        sizes = [list(hook.stored[1]) for hook in hooks if hook.stored is not None]
        mods = [hook.stored[0] for hook in hooks if hook.stored is not None]
    idxs = np.argsort([mod.k for mod in mods])
    return np.array(sizes, dtype=object)[idxs], np.array(mods, dtype=object)[idxs]

# Cell
def gaussian_mask(m, s, d, R, C):
    # indices to create centers
    R = torch.arange(R, dtype=torch.float32, device=m.device).reshape((1, R, 1))
    C = torch.arange(C, dtype=torch.float32, device=m.device).reshape((1, 1, C))
    centers = m[:, None, None] + R * d[:, None, None]
    column_centers = C - centers
    mask = torch.exp(-.5 * torch.square(column_centers / s[:, None, None]))
    # we add eps for numerical stability
    normalised_mask = mask / (mask.sum(-1, keepdims=True) + 1e-8)
    return normalised_mask

# Cell
def get_num_features(model):
    sizes, _ = get_sizes(model)
    return sizes[-1, 1]