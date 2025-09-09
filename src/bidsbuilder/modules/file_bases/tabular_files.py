import pandas as pd

from ...util.io import _write_json, _write_tsv
from ..core.dataset_core import DatasetCore
from ...util.hooks import *
from pandas.api.types import infer_dtype
from attrs import define, field
from typing import TYPE_CHECKING, ClassVar, Any, Union
from ..schema_objects import Column

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class columnView(MinimalSet):
    data:pd.DataFrame = field(init=False, factory=pd.DataFrame)
    col_names:set = field(set)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.col_names = set(self.data.columns.to_list())
        return

    def __getitem__(self, col_name):
        return self.data[col_name].to_list()

    def __contains__(self, value):
        return value in self.col_names

def make_column_view(instance:'tabularFile', descriptor):
    return columnView

@define(slots=True)
class tabularFile(DatasetCore):
    data:pd.DataFrame = field(init=False, factory=pd.DataFrame)
    columns:ClassVar[MinimalDict[str, Column]] = HookedDescriptor(columnView,factory=make_column_view,tags="columns")

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        return

    def _make_file(self, force:bool):
        _write_tsv(self._tree_link.path, self.data, force)

    @property
    def json_sidecar(self):
        return self._tree_link.parent.fetch(".json")

    def addColumn(self):
        pass
    """
    TODO:
        rules.tabular_data.*

selectors - List of expressions; any evaluating false indicate rule does not apply
columns - Object with keys that may be found in objects.columns, values either a requirement level or an object
initial_columns - An optional list of columns that must be the first N columns of a file
index_columns - An optional list of columns that uniquely identify a row.
additional_columns - Indicates whether additional columns may be defined. One of allowed, allowed_if_defined and not_allowed.
    
    allow for setting of initial column

    index column

    as well as using additional_column as a validator for columns

    Maybe set columns as a hooked descriptor with a callback to update the sidecar_json if columns are added

    and a validator when adding columns based on wether it is allowed (additional_columns) etc..
    """

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



class tabularJSONFile(DatasetCore):
    pass

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

def _set_tabular_schema(schema:'Namespace'):
    tabularJSONFile._schema = schema.rules.tabular_data
    tabularJSONFile._recurse_depth = 2