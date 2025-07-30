
from typing import TYPE_CHECKING
from ...modules.core.dataset_core import DatasetCore

if TYPE_CHECKING:
    from ...main_module import BidsDataset

def schema(core:DatasetCore, add_callbacks:bool=False):
    ...

def dataset(core:DatasetCore, add_callbacks:bool=False) -> 'BidsDataset':
    return core._dataset

def subject(core:DatasetCore, add_callbacks:bool=False):
    ...

def path(core:DatasetCore, add_callbacks:bool=False) -> str:
    return core._tree_link.relative_path

def entities(core:DatasetCore, add_callbacks:bool=False):
    return
    ...

def datatype(core:DatasetCore, add_callbacks:bool=False):
    return
    ...

def suffix(core:DatasetCore, add_callbacks:bool=False):
    return
    ...

def extension(core:DatasetCore, add_callbacks:bool=False):
    return
    ...

def modality(core:DatasetCore, add_callbacks:bool=False):
    ...

def sidecar(core:DatasetCore, add_callbacks:bool=False):
    ...

def associations(core:DatasetCore, add_callbacks:bool=False):
    ...

def columns(core:DatasetCore, add_callbacks:bool=False):
    
    ...

def json(core:DatasetCore, add_callbacks:bool=False):
    """   NOT YET COMPLETED NEED TO MAKE A MORE ROBUST METHOD
    WHICH TAKES INTO ACCOUNT THE INHERITANCE PRINCIPLE IN ORDER TO COLLECT ALL METADATA
    """
    from ...modules.file_bases.json_files import JSONfile
    if not isinstance(core, JSONfile):
        return None
    else:
        return core

def gzip(core:DatasetCore, add_callbacks:bool=False):
    ...

def nifti_header(core:DatasetCore, add_callbacks:bool=False):
    ...

def ome(core:DatasetCore, add_callbacks:bool=False):
    ...

def tiff(core:DatasetCore, add_callbacks:bool=False):
    ...

__all__ = ["schema","dataset","subject","path","entities","datatype","suffix","extension","modality",
           "sidecar","associations","columns","json","gzip","nifti_header","ome","tiff"]

def notImplemented(*args, **kwargs):
    raise NotImplementedError()

#
# The context provides the namespaces available to rules.
# These namespaces are used by selectors to define the scope of application
# for a rule, as well as assertions, to determine whether the rule is satisfied.
#
# Not all components of the context will be defined; for example a NIfTI header
# will only be defined when examining a NIfTI file.
#
# The dataset namespace is constructed once and is available when visiting all
# files.
#
# The subject namespace is constructed once per subject, and is available when
# visiting all files within that subject.
#
# All other (current) namespaces are defined on individual files.
# Sidecar metadata and file associations are built according to the inheritance
# principle.
#