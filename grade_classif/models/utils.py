#AUTOGENERATED! DO NOT EDIT! File to edit: dev/22_models_utils.ipynb (unless otherwise specified).

__all__ = ['named_leaf_modules', 'get_sizes']

#Cell
import torch
from ..core import ifnone
import numpy as np

#Cell
def named_leaf_modules(name, model):
    named_children = list(model.named_children())
    if named_children==[]:
        return [(name, model)]
    else:
        res = []
        for n, m in named_children:
            pref = name+'.' if name != '' else ''
            res += named_leaf_modules(pref+n, m)
        return res

#Cell
def get_sizes(model, input_shape=(3, 224, 224), leaf_modules=None):
    sizes = []
    size_handles = []
    leaf_modules = ifnone(leaf_modules, named_leaf_modules('', model))

    def _hook(model, input, output):
        sizes.append((model, input[0].shape[1:], output.shape[1:]))

    for n, m in leaf_modules:
        m.name = n
        size_handles.append(m.register_forward_hook(_hook))

    x = torch.rand(2, *input_shape)
    model.eval()(x)
    for handle in size_handles:
        handle.remove()
    return np.array(sizes)