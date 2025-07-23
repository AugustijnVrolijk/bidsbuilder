
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bidsschematools.types import Namespace
    from ..main_module import BidsDataset

def set_all_schema_(dataset:'BidsDataset',schema:'Namespace'):
    from .dataset_core import _set_dataset_core
    _set_dataset_core(dataset)
    from .schema_objects import _set_object_schemas
    _set_object_schemas(schema)
    from .filenames import _set_filenames_schema
    _set_filenames_schema(schema)
    from .directories import _set_folder_schemas
    _set_folder_schemas()
    from .tabular_files import _set_tabular_schema
    _set_tabular_schema(schema)
    from .json_files import _set_JSON_schema
    _set_JSON_schema(schema)