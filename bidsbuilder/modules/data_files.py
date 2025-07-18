from ..util.categoryDict import categoryDict
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

    _metadata:categoryDict[str, (str, Metadata)] = field(init=False, default=categoryDict())
    _removed_key:dict = field(init=False, default=dict()) #for overflow values passed to json which doesn't have a valid key representing it
    _cur_labels:set = field(init=False, default=set())

    def _make_file(self):
        pass

    def __getattr__(self, name:str):
        if name.startswith("_"):  # treat as attribute
            return self.__dict__[name]
        else:  # treat as metadata key
            return self._metadata[name]
    
    def  __setattr__(self, name:str, value:Any):
        if name.startswith("_"):  # treat as attribute
            self.__dict__[name] = value
        else:  # treat as metadata key
            self._metadata[name] = value
    
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

class sidecar_JSONfile(JSONfile):
    pass

class extra_JSONfile(JSONfile):
    pass

class agnostic_JSONfile(JSONfile):
    #allows to set the schema for a different area
    pass


"""

def process_metadata(schema):
    iterate over schema:
    
    if selectors are valid:
        process fields

def process_fields(Namespace):
    create metadata dict from fields, i.e.
    for each key:
        check if its values is a value, or another namespace
"""

def _set_JSON_schema(schema:'Namespace'):
    agnostic_JSONfile._schema = schema.rules.dataset_metadata
    #sidecar_JSONfile._schema
    #extra_JSONfile._schema 