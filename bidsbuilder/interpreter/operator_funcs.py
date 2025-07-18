from typing import Any, TYPE_CHECKING
from bidsbuilder.interpreter.evaluation_funcs import checkNone

if TYPE_CHECKING:
    from bidsbuilder.modules.dataset_core import DatasetCore

@checkNone
def get_property(core:'DatasetCore', prop:str):

    return notImplemented()

@checkNone
def get_list_index(arr:list, idx:int) -> Any:
    assert isinstance(arr, list), "arr needs to be of type list for get_list_index"
    assert isinstance(idx, int), "idx needs to be of type int for get_list_index"
    assert idx <= len(arr), "index out of bounds"

    return arr[idx]

def wrap_list(*args):
    return [*args]

@checkNone
def contains(val:str, ref:'DatasetCore') -> bool:
    #can use the __contains__ 
    return val in ref

@checkNone
def op_and(a, b):
    return a and b

@checkNone
def op_or(a, b):
    return a or b

def notImplemented(*args, **kwargs):
    raise NotImplementedError()

__all__ = ["notImplemented", "get_property", "get_list_index", "wrap_list", "contains","op_and","op_or"]