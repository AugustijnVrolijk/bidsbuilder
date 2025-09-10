import pandas as pd
import pandera.pandas as pa

from ...util.io import _write_json, _write_tsv
from ..core.dataset_core import DatasetCore
from ...util.hooks import *
from pandas.api.types import infer_dtype
from attrs import define, field
from typing import TYPE_CHECKING, ClassVar, Any, Union
from ..schema_objects import Column
from ...schema.schema_checking import TSV_check_schema

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class columnView(MinimalSet):
    data:pd.DataFrame = field(init=False, factory=pd.DataFrame)
    data_schema:pa.DataFrameSchema = field(init=False, factory=lambda: pa.DataFrameSchema({}))
    col_names:dict[str, Column] = HookedDescriptor(dict)

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


"""
columnView is what to return for the interpreter column attribute. i.e. its a list of columns, 
and gives access to the specific dataframe column as a list with getitem

have tableview encapsulate the actual dataframe, with support for initial column, which are allowed to add etc...
and a dataschema for validation of the dataframe inputs
"""

@define(slots=True)
class tableView():
    data:pd.DataFrame = field(init=False, factory=pd.DataFrame) # at the moment will not 
    data_schema:pa.DataFrameSchema = field(init=False, factory=lambda: pa.DataFrameSchema({}))
    columns:dict

    @classmethod
    def create(cls):
        ...

    def add(): ...


@define(slots=True)
class tabularFile(DatasetCore):
    
    _n_schema_true:int = field(init=False, default=0) #number of times schema has been applied
    data:pd.DataFrame = field(init=False, factory=pd.DataFrame) # at the moment will not 
    data_schema:pa.DataFrameSchema = field(init=False, factory=lambda: pa.DataFrameSchema({}))
    


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

def _set_tabular_schema(schema:'Namespace'):
    tabularJSONFile._schema = schema.rules.tabular_data
    tabularJSONFile._recurse_depth = 2