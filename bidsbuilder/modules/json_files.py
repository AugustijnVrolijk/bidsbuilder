from ..util.categoryDict import categoryDict
from ..util.io import _write_JSON
from .schema_objects import Metadata
from .dataset_core import DatasetCore

from attrs import define, field
from typing import TYPE_CHECKING, ClassVar, Any

if TYPE_CHECKING:
    from ..interpreter.selectors import selectorHook
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class JSONfile(DatasetCore):
    
    _schema:ClassVar['Namespace']

    _metadata:categoryDict = field(init=False, default=categoryDict())
    _removed_key:dict = field(init=False, default=dict()) #for overflow values passed to json which doesn't have a valid key representing it
    _cur_labels:set = field(init=False, default=set())

    def __attrs_post_init__(self):
        print("hello")

    def __post_init__(self):
        self._check_schema()

    def _make_file(self, force:bool):
        final_json = {}
        for key, val in self._metadata.items():
            cat, val = val
            if val is None:
                match cat:
                    case "required":
                        pass
                    case "recommended":
                        final_json[key] = "MISSING"
                    case "optional":
                        pass
            else:
                final_json[key] = val.val
        _write_JSON(self._tree_link.path, final_json, force)

    def __getitem__(self, name:str):
        return self._metadata[name]
    
    def  __setitem__(self, name:str, value:Any):
        self._metadata[name] = value
    
    def __contains__(self, key):
        return (key in self._metadata.keys())

    def _check_schema(self):

        for key in self._schema.keys():
            cur_selector:'selectorHook' = self._schema[key]["selectors"]
            if cur_selector(self):
                metadata_dict = self._process_fields(self._schema[key]["fields"])
                self._add_metadata_keys(metadata_dict, key)
            elif key in self._cur_labels:
                self._remove_metadata_keys(self._schema[key]["fields"], key)

    def _add_metadata_keys(self, to_add:dict, label:str):
        self._metadata._populate_dict(to_add)
        self._cur_labels.add(label)

    def _remove_metadata_keys(self, to_remove:'Namespace', label:str):
        self._cur_labels.remove(label)

        for key in to_remove.keys():
            try:
                removed = self._metadata.pop(key)
                self._removed_key[key] = removed
            except:
                continue

    @classmethod
    def _process_fields(cls, fields:'Namespace') -> dict:
        
        processed = {}
        for key in fields.keys():
            if isinstance(fields[key], str): #the value is a requirement
                processed[key] = (fields[key], Metadata(key, None))
            else:
                level = fields[key].pop("level")
                met_instance = Metadata(key, None)
                Metadata._override[met_instance] = fields[key]
                processed[key] = (level, met_instance)
        return processed


@define(slots=True)
class sidecar_JSONfile(JSONfile):
    pass

@define(slots=True)
class extra_JSONfile(JSONfile):
    pass

@define(slots=True)
class agnostic_JSONfile(JSONfile):
    pass

def _set_JSON_schema(schema:'Namespace'):
    agnostic_JSONfile._schema = schema.rules.dataset_metadata
    sidecar_JSONfile._schema = schema.rules.sidecars
    extra_JSONfile._schema = schema.rules.json