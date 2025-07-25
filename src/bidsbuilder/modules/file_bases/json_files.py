from ...util.categoryDict import categoryDict
from ...util.io import _write_JSON
from ..core.dataset_core import DatasetCore
from ...schema.schema_parsing import JSON_check_schema

from attrs import define, field
from typing import TYPE_CHECKING, ClassVar, Any, Generator


if TYPE_CHECKING:
    from ...schema.interpreter.selectors import selectorHook
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class JSONfile(DatasetCore):
    
    _schema:ClassVar['Namespace']

    _metadata:categoryDict = field(init=False, factory=categoryDict)
    _removed_key:dict = field(init=False, factory=dict) #for overflow values passed to json which doesn't have a valid key representing it
    _cur_labels:set = field(init=False, factory=set)

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
        try:
            self._metadata[name] = value
        except KeyError:
            self._removed_key[name] = value
            
    def __contains__(self, key):
        return (key in self._metadata.keys())

    def _check_schema(self, add_callbacks:bool=False):
        """
        check 
        """
        # we use a generator (JSON_check_schema) in order to adhere to the top down logic
        # (schema assumes top down parsing)

        for flag, label, items in JSON_check_schema(self, self._schema,self._cur_labels, add_callbacks):
            
            if flag == "add":
                self._add_metadata_keys(items, label)
            elif flag == "del":
                self._remove_metadata_keys(items, label)
            else:
                raise RuntimeError(f"unknown flag: {flag} given in {self}._check_schema")
            
        self._check_removed()

    def _check_removed(self):
        for key, val in self._removed_key.items():
            if key in self._metadata:
                if isinstance(val, tuple):
                    _, val = val
                self._metadata[key] = val

    def _add_metadata_keys(self, to_add:dict, label:str):
        self._metadata._populate_dict(to_add)
        self._cur_labels.add(label)

    def _remove_metadata_keys(self, to_remove:list, label:str):
        self._cur_labels.remove(label)

        for key in to_remove:
            removed = self._metadata.pop(key)
            self._removed_key[key] = removed

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
