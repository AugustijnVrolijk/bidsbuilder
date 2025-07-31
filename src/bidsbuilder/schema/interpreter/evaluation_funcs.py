import re

from typing import Any, Union, TYPE_CHECKING
from functools import wraps
from ...modules.core.dataset_tree import FileEntry

if TYPE_CHECKING:
    from bidsbuilder.modules.core.dataset_core import DatasetCore


def checkNone(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check all positional and keyword arguments for None
        if any(arg is None for arg in args) or any(value is None for value in kwargs.values()):
            return None
        return func(*args, **kwargs)
    return wrapper

@checkNone
def count(arg:list, val:Any) -> int:
    """
    Number of elements in an array equal to val

    count(columns.type, "EEG")

    The number of times “EEG” appears in the column “type” of the current TSV file
    """
    assert isinstance(arg, list), f"arg {arg} is not of type list for function count"

    return sum(1 for x in arg if x == val)

@checkNone
def exists(core:'DatasetCore', arg:Union[str|list], rule:str, add_callbacks:bool=False) -> int:
    """
    Count of files in an array that exist in the dataset. String is array with length 1. See following section for the meanings of rules.

    exists(sidecar.IntendedFor, "subject")

    True if all files in IntendedFor exist, relative to the subject directory.
    """

    if isinstance(arg, str):
        arg = [arg]

    assert isinstance(arg, list), f"arg {arg} is not of type list for function exists"
    assert isinstance(rule, str), f"rule {rule} is not of type str for function exists"

    #find the correct reference
    if rule == "dataset":
        reference = core._dataset.tree
    elif rule == "subject":
        return notImplemented()
    elif rule == "stimuli":
        reference = core._dataset._tree_reference.fetch(r"/stimuli", False)
    elif rule == "file":
        reference = core._tree_link
        #fileTree objects are directories, UserFileEntry can be both (Filetree inherits it)
        if not isinstance(reference, FileEntry):
            reference = reference.parent
    elif rule == "bids-uri":
        return notImplemented()
    else:
        raise ValueError(f"{rule} not a valid rules, please see https://bidsschematools.readthedocs.io/en/latest/description.html#the-exists-function")
    
    count = 0
    for path in arg:
        obj = reference.fetch(path)
        if add_callbacks:
            cls = obj.__class__
            getattr(cls, "exists").add_callback(obj, core._check_schema)
        if obj:
            count += obj.exists

    return count

@checkNone
def index(arg:list, val:Any) -> int:
    """
    Index of first element in an array equal to val, null if not found

    index(["i", "j", "k"], axis)

    The number, from 0-2 corresponding to the string axis
    """
    assert isinstance(arg, list), f"arg {arg} is not of type list for function index"

    try:
        retVal = arg.index(val)
    except:
        retVal = None

    return retVal

@checkNone
def intersects(a:list, b:list) -> Union[list, bool]:
    """
    The intersection of arrays a and b, or false if there are no shared values.

    intersects(dataset.modalities, ["pet", "mri"])

    Non-empty array if either PET or MRI data is found in dataset, otherwise false
    """
    assert isinstance(a, list), f"a {a} is not of type list for function intersects"
    assert isinstance(b, list), f"b {b} is not of type list for function intersects"

    final = []
    for x in a:
        if x in b:
            final.append(x)
    
    #empty lists are "False" in python
    if not final:
        final = False

    return final

@checkNone
def allequal(a:list, b:list) -> bool:
    """
    true if arrays have the same length and paired elements are equal

    #the given example is taken frfom the schema at v1.10.0 and is not clear as it uses the wrong function...
    
    intersects(dataset.modalities, ["pet", "mri"])

    True if either PET or MRI data is found in dataset
    
    #my interpretation represents the first line describing functionality rather than the example
    """
    assert isinstance(a, list), f"a {a} is not of type list for function allequal"
    assert isinstance(b, list), f"b {b} is not of type list for function allequal"

    for i,x in enumerate(a):
        if x != b[i]:
            return False

    return True

@checkNone
def length(arg:list) -> int:
    """
    Number of elements in an array

    length(columns.onset) > 0

    True if there is at least one value in the onset column
    """

    assert isinstance(arg, list), f"arg {arg} is not of type list for function length"

    return len(arg)

@checkNone
def nMatch(arg:str, pattern:str) -> bool:
    """
    true if arg matches the regular expression pattern (anywhere in string)

    match(extension, ".gz$")

    True if the file extension ends with .gz
    """

    assert isinstance(arg, str), f"arg {arg} is not of type str for function match"
    assert isinstance(pattern, str), f"pattern {pattern} is not of type str for function match"

    return bool(re.search(pattern, arg))

@checkNone
def max(arg:list) -> int:
    """
    The largest non-n/a value in an array

    max(columns.onset)

    The time of the last onset in an events.tsv file
    """
    assert isinstance(arg, list), f"arg {arg} is not of type list for function max"
    if len(arg) == 0:
        return None

    i = 0
    while not isinstance(arg[i], int):
        i += 1
        if i > len(arg):
            return None

    max_val = arg[i]
    for j in range(i, length(arg)):
        if not isinstance(arg[j], int):
            continue
        if arg[j] > max_val:
            max_val = arg[j]

    return max_val

@checkNone
def min(arg:list) -> int:
    """
    The smallest non-n/a value in an array

    min(sidecar.SliceTiming) == 0

    A check that the onset of the first slice is 0s
    """
    assert isinstance(arg, list), f"arg {arg} is not of type list for function min"
    if len(arg) == 0:
        return None

    i = 0
    while not isinstance(arg[i], int):
        i += 1
        if i > len(arg):
            return None

    min_val = arg[i]
    for j in range(i, length(arg)):
        if not isinstance(arg[j], int):
            continue
        if arg[j] < min_val:
            min_val = arg[j]

    return min_val

def sorted(arg:list, method:str) -> list:
    """
    The sorted values of the input array; defaults to type-determined sort. If method is “lexical”, or “numeric” use lexical or numeric sort.

    sorted(sidecar.VolumeTiming) == sidecar.VolumeTiming

    True if sidecar.VolumeTiming is sorted
    """
    return notImplemented()

@checkNone
def substr(arg:str, start:int, end:int) -> str:
    """    
    The portion of the input string spanning from start position to end position

    substr(path, 0, length(path) - 3)

    path with the last three characters dropped
    """
    assert isinstance(arg, str), f"arg {arg} is not of type str for function substr"
    assert isinstance(start, int), f"start {start} is not of type int for function substr"
    assert isinstance(end, int), f"end {end} is not of type int for function substr"

    return arg[start:end]

def nType(arg:Any) -> str:
    """
    The name of the type, including "array", "object", "null"

    type(datatypes)

    Returns "array"
    """
    if isinstance(arg, list):
        return "array"
    elif isinstance(arg, object):
        return "object"
    elif arg is None:
        return "null"
    return notImplemented()

def notImplemented(*args, **kwargs):
    raise NotImplementedError()

__all__ = ["count", "exists", "index", "intersects", "allequal", "length", "nMatch", "max", "min", "sorted", "substr", "nType"]

