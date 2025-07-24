from ...util.categoryDict import categoryDict
from ...util.io import _write_JSON
from ..schema_objects import Metadata
from ..core.dataset_core import DatasetCore

from attrs import define, field
from typing import TYPE_CHECKING, ClassVar, Any, Generator


if TYPE_CHECKING:
    from ...schema.interpreter.selectors import selectorHook
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class JSONfile(DatasetCore):
    
    _schema:ClassVar['Namespace']
    _recurse_depth:ClassVar[int]

    _metadata:categoryDict = field(init=False, factory=categoryDict)
    _removed_key:dict = field(init=False, factory=dict) #for overflow values passed to json which doesn't have a valid key representing it
    _cur_labels:set = field(init=False, factory=set)

    def __post_init__(self):
        self._check_schema()

    def _make_file(self, force:bool):
        final_json = {}
        for key, val in self._metadata.items():
            cat, val = val
            if val.val is None:
                match cat:
                    case "required":
                        final_json[key] = "MISSING"
                        pass
                    case "recommended":
                        pass
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

    def _check_schema(self, schema=None):
        if schema is None:
            schema = self._schema

        for label, _sub_schema in self._recurse_schema_explore():
            cur_selector:'selectorHook' = _sub_schema["selectors"]
            if cur_selector(self):
                metadata_dict = self._process_fields(_sub_schema["fields"])
                self._add_metadata_keys(metadata_dict, label)
            elif label in self._cur_labels:
                self._remove_metadata_keys(_sub_schema["fields"], label)

    @classmethod
    def _recurse_schema_explore(cls, schema = None, depth = 0) -> Generator:
        """
        Recursively yield schema keys up to cls._recurse_depth levels.
        """
        if schema is None:
            schema = cls._schema

        for key, value in schema.items():
            if depth + 1 == cls._recurse_depth:
                yield key, value
            else:
                yield from cls._recurse_schema_explore(value, (depth + 1))

    def _add_metadata_keys(self, to_add:dict, label:str):
        self._metadata._populate_dict(to_add)
        self._cur_labels.add(label)

    def _remove_metadata_keys(self, to_remove:'Namespace', label:str):
        self._cur_labels.remove(label)

        for key in to_remove.keys():
            removed = self._metadata.pop(key)
            self._removed_key[key] = removed


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
    agnostic_JSONfile._recurse_depth = 1

    sidecar_JSONfile._schema = schema.rules.sidecars
    sidecar_JSONfile._recurse_depth = 2

    extra_JSONfile._schema = schema.rules.json
    sidecar_JSONfile._recurse_depth = 2
