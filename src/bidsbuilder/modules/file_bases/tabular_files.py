from ..schema_objects import Metadata
from ..core.dataset_core import UnknownFile
from .json_files import JSONfile

from attrs import define, field
from typing import TYPE_CHECKING, ClassVar, Any

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class tabularFile(UnknownFile):
    
    pass

class tabularJSONFile(JSONfile):
    #no need to differentiate between agnostic and not, they are all in the same dir.
    #may be slightly ineffecient
    pass

def _set_tabular_schema(schema:'Namespace'):
    tabularJSONFile._schema = schema.rules.tabular_data
    tabularJSONFile._recurse_depth = 2