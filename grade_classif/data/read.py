#AUTOGENERATED! DO NOT EDIT! File to edit: dev/10_data_read.ipynb (unless otherwise specified).

__all__ = ['get_items', 'get_scan']

#Cell
from ..core import ifnone

#Cell
def _check_include(obj, include):
    return include is None or obj.name in include

#Cell
def _check_exclude(obj, exclude):
    return exclude is None or obj.name not in exclude

#Cell
def _check_valid(obj, include, exclude):
    return _check_include(obj, include) and _check_exclude(obj, exclude) and not obj.name.startswith('.')

#Cell
def get_items(folder, label_func, recurse=True, extensions=None, include=None, exclude=None, filterfunc=None):
    items = []
    labels = []
    filterfunc = ifnone(filterfunc, lambda x: True)
    for obj in folder.iterdir():
        if obj.is_file():
            if extensions is None or obj.suffix in extensions and filterfunc(obj):
                items.append(obj)
                labels.append(label_func(obj))
        elif recurse and _check_valid(obj, include, exclude):
            items_r, labels_r = get_items(obj, label_func, extensions=extensions, filterfunc=filterfunc)
            items += items_r
            labels += labels_r
    return items, labels

#Cell
def get_scan(folder, scan_name, include=None, exclude=None):
    dirs = []
    for item in folder.iterdir():
        if item.name == 'scan_name' and _check_valid(item, include, exclude):
            return item
        if item.is_dir():
            dirs.append(item)
    for item in dirs:
        obj = get_scan(item, scan_name)
        if obj is not None:
            return obj