
from typing import TYPE_CHECKING
from bidsbuilder.modules.coreModule import DatasetCore

if TYPE_CHECKING:
    from bidsbuilder.bidsDataset import BidsDataset

def schema():
    return notImplemented()

def dataset(core:'DatasetCore') -> 'BidsDataset':
    return core.dataset

def subject():
    return notImplemented()

def path(core:DatasetCore) -> str:
    assert isinstance(core, DatasetCore)
    return core._tree_reference.relative_path

def entities():
    return notImplemented()

def datatype():
    return notImplemented()

def suffix():
    return notImplemented()

def extension():
    return notImplemented()

def modality():
    return notImplemented()

def sidecar():
    return notImplemented()

def associations():
    return notImplemented()

def columns():
    return notImplemented()

def json():
    return notImplemented()

def gzip():
    return notImplemented()

def nifti_header():
    return notImplemented()

def ome():
    return notImplemented()

def tiff():
    return notImplemented() 

__all__ = ["schema","dataset","subject","path","entities","datatype","suffix","extension","modality",
           "sidecar","associations","columns","json","gzip","nifti_header","ome","tiff"]

def notImplemented(*args, **kwargs):
    raise NotImplementedError()
