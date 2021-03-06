# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/10_data.read.ipynb (unless otherwise specified).

__all__ = ['get_files', 'get_leaf_folders', 'get_items', 'get_scan', 'split', 'create_csv']

# Cell
from ..core import ifnone
from ..imports import *
from fastcore.foundation import L, setify

# Cell
def _check_include(obj: Path, include: Sequence[str]) -> bool:
    return include is None or obj.name in include

# Cell
def _check_exclude(obj: Path, exclude: Sequence[str]) -> bool:
    return exclude is None or obj.name not in exclude

# Cell
def _check_valid(obj: Path, include: Sequence[str], exclude: Sequence[str]) -> bool:
    return (
        _check_include(obj, include)
        and _check_exclude(obj, exclude)
        and not obj.name.startswith(".")
    )

# Cell
def _get_files(p, fs, extensions=None):
    p = Path(p)
    res = [
        p / f
        for f in fs
        if not f.startswith(".")
        and ((not extensions) or f'.{f.split(".")[-1].lower()}' in extensions)
    ]
    return res


def get_files(path, extensions=None, recurse=True, folders=None, followlinks=True):
    """
    Find all files in a folder recursively.
    Arguments:
        path (str): Path to input folder.
        extensions (list of str): list of acceptable file extensions.
        recurse (bool): whether to perform a recursive search or not.
        folders (list of str): direct subfolders to explore (if None explore all).
        followlinks (bool): whether to follow symlinks or not.
    Returns:
        list: list of all absolute paths to found files.
    """
    path = Path(path)
    folders = L(folders)
    extensions = setify(extensions)
    extensions = {e.lower() for e in extensions}
    if recurse:
        res = []
        for i, (p, d, f) in enumerate(
            os.walk(path, followlinks=followlinks)
        ):  # returns (dirpath, dirnames, filenames)
            if len(folders) != 0 and i == 0:
                d[:] = [o for o in d if o in folders]
            else:
                d[:] = [o for o in d if not o.startswith(".")]
            if len(folders) != 0 and i == 0 and "." not in folders:
                continue
            res += _get_files(p, f, extensions)
    else:
        f = [o.name for o in os.scandir(path) if o.is_file()]
        res = _get_files(path, f, extensions)
    return L(res)

# Cell
def get_leaf_folders(path, folders=None, followlinks=True):
    path = Path(path)
    folders = L(folders)
    res = []
    for i, (p, d, f) in enumerate(
        os.walk(path, followlinks=followlinks)
    ):  # returns (dirpath, dirnames, filenames)
        if len(d) == 0 and not p.startswith("."):
            res.append(p)
            continue
        if len(folders) != 0 and i == 0:
            d[:] = [o for o in d if o in folders]
        else:
            d[:] = [o for o in d if not o.startswith(".")]
        if len(folders) != 0 and i == 0 and "." not in folders:
            continue
    return L(res)

# Cell
def get_items(
    folder: Union[Path, str],
    label_func: Callable[[Path], bool],
    recurse: bool = True,
    extensions: Optional[Sequence[str]] = None,
    include: Optional[Sequence[str]] = None,
    exclude: Optional[Sequence[str]] = None,
    filterfunc: Optional[Callable[[Path], bool]] = None,
) -> Tuple[List[Path], List[Path]]:
    items = []
    labels = []
    folder = Path(folder)
    filterfunc = ifnone(filterfunc, lambda x: True)
    for obj in folder.iterdir():
        if obj.is_file():
            if extensions is None or obj.suffix in extensions and filterfunc(obj):
                items.append(obj)
                labels.append(label_func(obj))
        elif recurse and _check_valid(obj, include, exclude):
            items_r, labels_r = get_items(
                obj, label_func, extensions=extensions, filterfunc=filterfunc
            )
            items += items_r
            labels += labels_r
    return items, labels

# Cell
def get_scan(
    folder: Union[Path, str],
    scan_name: str,
    include: Optional[Sequence[str]] = None,
    exclude: Optional[Sequence[str]] = None,
) -> Path:
    dirs = []
    folder = Path(folder)
    for item in folder.iterdir():
        if item.name == scan_name:
            return item
        if item.is_dir() and _check_valid(item, include, exclude):
            dirs.append(item)
    for item in dirs:
        obj = get_scan(item, scan_name)
        if obj is not None:
            return obj

# Cell
def split(
    scans: Sequence[str], grades: Sequence[str], valid_pct: float = 0.2
) -> List[str]:
    grades1 = list(filter(lambda x: x == "1", grades))
    order = np.random.permutation(len(scans))
    n = {"1": len(grades1), "3": len(grades) - len(grades1)}
    k = {"1": 0, "3": 0}
    splits = ["" for _ in scans]
    for o in order:
        grade, scan = grades[o], scans[o]
        if k[grade] >= valid_pct * n[grade]:
            split = "train"
        else:
            split = "valid"
        k[grade] += 1
        splits[o] = split
    return splits

# Cell
def _remove_doubles(
    scans: Sequence[str], grades: Sequence[str]
) -> Tuple[List[str], List[str]]:
    scans_res = []
    grades_res = []
    for scan, grade in zip(scans, grades):
        if scan not in scans_res:
            scans_res.append(scan)
            grades_res.append(grade)
    return scans_res, grades_res

# Cell
def create_csv(
    csv_path: Path, data_path: Path, label_func: Optional[Callable[[Path], bool]] = None
) -> pd.DataFrame:
    label_func = ifnone(label_func, lambda x: x.parts[-3])
    scans, grades = get_items(data_path, label_func, extensions=[".png"])
    scans = list(map(lambda x: x.parent.name, scans))
    scans, grades = _remove_doubles(scans, grades)
    splits = split(scans, grades)
    df = pd.DataFrame({"scan": scans, "grade": grades, "split": splits})
    df.to_csv(csv_path, index=False)
    return df