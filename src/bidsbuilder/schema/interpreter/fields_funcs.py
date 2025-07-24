
from typing import TYPE_CHECKING
from ...modules.core.dataset_core import DatasetCore

if TYPE_CHECKING:
    from ...main_module import BidsDataset

def schema():
    return notImplemented()

def dataset(core:'DatasetCore') -> 'BidsDataset':
    return core._dataset

def subject():
    return notImplemented()

def path(core:DatasetCore) -> str:
    return core._tree_link.relative_path

def entities(core:DatasetCore):
    return
    return notImplemented()

def datatype(core:DatasetCore):
    return
    return notImplemented()

def suffix(core:DatasetCore):
    return
    return notImplemented()

def extension(core:DatasetCore):
    return
    return notImplemented()

def modality():
    return notImplemented()

def sidecar():
    return notImplemented()

def associations():
    return notImplemented()

def columns():
    return notImplemented()

def json(core:DatasetCore):
    """   NOT YET COMPLETED NEED TO MAKE A MORE ROBUST METHOD
    WHICH TAKES INTO ACCOUNT THE INHERITANCE PRINCIPLE IN ORDER TO COLLECT ALL METADATA
    """
    from ...modules.file_bases.json_files import JSONfile
    assert isinstance(core, JSONfile), f"given core: {core} was not a JSON\n update fields_funcs.json to use inheritance principle"
    return core

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