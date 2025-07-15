from .commonFiles import coreJSON, coreTSV, coreUnknown, coreFolder
from .coreModule import DatasetCore
from .data_folders import Subject, Session
from .schema_objects import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bidsschematools.types import Namespace
    from ..bidsDataset import BidsDataset

from .data_folders import _set_folder_schemas
_set_folder_schemas()

def set_all_schema_(dataset:'BidsDataset',schema:'Namespace'):
    from .data_folders import _set_folder_dataset_ref
    _set_folder_dataset_ref(dataset)
    from .schema_objects import _set_object_schemas
    _set_object_schemas(schema)
    from .coreModule import _set_dataset_core
    _set_dataset_core(dataset)

#__all__ = ["DatasetCore", "coreJSON", "coreTSV", "coreUnknown", "coreFolder", "Subject", "Session", "Entity"]