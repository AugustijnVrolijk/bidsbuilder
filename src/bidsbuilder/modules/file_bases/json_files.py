from ...util.categoryDict import categoryDict
from ...util.io import _write_JSON
from ..core.dataset_core import DatasetCore
from ...schema.schema_checking import JSON_check_schema
from ...util.hooks import HookedDescriptor
from attrs import define, field
from typing import TYPE_CHECKING, ClassVar, Any, Union
from ..schema_objects import Metadata

if TYPE_CHECKING:
    from ...schema.interpreter.selectors import selectorHook
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class JSONfile(DatasetCore):
    
    _schema:ClassVar['Namespace']
    metadata:ClassVar[dict[str, 'Metadata']] = HookedDescriptor(dict)

    _metadata:dict[str, 'Metadata'] = field(init=False, factory=dict)
    _removed_key:dict[str, Any] = field(init=False, factory=dict) #for overflow values passed to json which doesn't have a valid key representing it
    _cur_labels:set = field(init=False, factory=set)
    

    def _make_file(self, force:bool):
        final_json = {}
        for key, value in self.metadata.items():
            cat, val = value.level, value.val
            if val is None:
                match cat:
                    case "required":
                        final_json[key] = "MISSING"
                    case "recommended":
                        pass
                    case "optional":
                        pass
            else:
                final_json[key] = val

        _write_JSON(self._tree_link.path, final_json, force)

    def __getitem__(self, key:str):
        return self._metadata[key].val
    
    def  __setitem__(self, key:str, value:Any):
        """
        Keys cannot be set using setitem. This ensures keys have been set via _add_metadata_keys enforcing categories to be specified
        """
        if key in self.metadata: 
            self.metadata[key].val = value
        else:
            if isinstance(value, Metadata):
                value = value.val
            self._removed_key[key] = value
            
    def __contains__(self, key):
        return (key in self._metadata.keys())

    def _check_schema(self, add_callbacks:bool=False, tags:Union[list,str] = None):
        """
        check the schema for the given object. 
        add_callbacks defines whether to add callbacks when checking the schema
        tags defines which selectors to check, enables skipping of irrelevant selectors or those unchanged
        """
        # we use a generator (JSON_check_schema) in order to adhere to the top down logic
        # (schema assumes top down parsing)
        modified = False
        for flag, label, items in JSON_check_schema(self, self._schema,self._cur_labels, add_callbacks, tags):
            modified = True
            if flag == "add":
                self._add_metadata_keys(items, label)
            elif flag == "del":
                self._remove_metadata_keys(items, label)
            else:
                raise RuntimeError(f"unknown flag: {flag} given in {self}._check_schema")
        
        if modified:
            self._check_removed()

    def _check_removed(self):
        for key, val in self._removed_key.items():
            if key in self.metadata:
                self.metadata[key].val = val

    def _add_metadata_keys(self, to_add:dict, label:str):
        self.metadata.update(to_add)
        self._cur_labels.add(label)

    def _remove_metadata_keys(self, to_remove:list, label:str):
        self._cur_labels.remove(label)

        for key in to_remove:
            removed = self.metadata.pop(key)
            self._removed_key[key] = removed.val

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
