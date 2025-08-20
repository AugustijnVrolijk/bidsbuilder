from ...util.categoryDict import categoryDict
from ...util.io import _write_json
from ..core.dataset_core import DatasetCore
from ...schema.schema_checking import JSON_check_schema
from ...util.hooks import HookedDescriptor, DescriptorProtocol
from attrs import define, field
from typing import TYPE_CHECKING, ClassVar, Any, Union, Self
from ..schema_objects import Metadata

if TYPE_CHECKING:
    from ...schema.interpreter.selectors import selectorHook
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class JSONfile(DatasetCore):
    
    _schema:ClassVar['Namespace']
    metadata:ClassVar[dict[str, 'Metadata']]

    _metadata:dict[str, 'Metadata'] = field(init=False, factory=dict)
    _removed_key:dict[str, Any] = field(init=False, factory=dict) #for overflow values passed to json which doesn't have a valid key representing it
    _cur_labels:set = field(init=False, factory=set)

    def _make_file(self, force:bool):
        _write_json(self._tree_link.path, self.rawMetadata, force)

    def __getitem__(self, key:str):
        return self._metadata[key].val

    def  __setitem__(self, key:str, value:Any):
        """
        Keys cannot be set using setitem. This ensures keys have been set via _add_metadata_keys enforcing categories to be specified
        """
        if isinstance(value, Metadata):
            value = value.val

        try:
            self.metadata[key].val = value
        except KeyError:
            self._removed_key[key] = value
    
    @property
    def rawMetadata(self):
        final_json = {}
        for key, value in self.metadata.items():
            cat, val = value.level, value.val
            if val is None:
                match cat:
                    case "required":
                        final_json[key] = None
                    case "recommended":
                        pass
                    case "optional":
                        pass
            else:
                final_json[key] = val
        return final_json

    @staticmethod
    def _metadata_validator(self:Self, descriptor:DescriptorProtocol, value:tuple[str, Any]):
        key, val = value
        """
        Keys cannot be set using setitem. This ensures keys have been set via _add_metadata_keys enforcing only correct metadata
        """
        if key not in getattr(self, descriptor.name):
            raise KeyError(f"key: {key} not found in metadata dict: {getattr(self, descriptor.name)}")
        else:
            return val

    metadata:ClassVar[dict[str, 'Metadata']] = HookedDescriptor(dict, fval=_metadata_validator) # considered making rawMetadata the getter
    # but this leads to all sorts of confusion if people did something like myJson.metadata[key] = value. As it would then not
    # actually modify the structure, but the "raw" dict spat out by rawMetadata

    def __contains__(self, key):
        return key in self.metadata

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
        self.metadata._data.update(to_add)
        self.metadata._check_callback()
        self._cur_labels.add(label)

    def _remove_metadata_keys(self, to_remove:list, label:str):
        self._cur_labels.remove(label)

        self.metadata._frozen = True
        for key in to_remove:
            removed = self.metadata.pop(key)
            self._removed_key[key] = removed.val
        self.metadata._frozen = True
        self.metadata._check_callback()

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
