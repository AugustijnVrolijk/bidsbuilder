import pandas as pd
import pandera.pandas as pa
from pandas.api.types import infer_dtype
from attrs import define, field
from typing import TYPE_CHECKING, ClassVar, Any, Union, Generator, Self

from ...util.io import _write_json, _write_tsv
from ..core.dataset_core import DatasetCore
from ...util.hooks import *
from ..schema_objects import Column
from ...schema.schema_checking import check_schema

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
    data_schema:pa.DataFrameSchema = field()
    data:pd.DataFrame = field() # at the moment will not 
    index_columns:set = field()
    additional_columns_flag = field() #allowed, allowed_if_defined, not_allowed
    columns:dict = field()
    

    @classmethod
    def create(cls, columns:dict, additional_columns_flag:str, initial_columns:list=None, index_columns:list=None) -> Self:
        """
        columns: - dict with values that may be found in objects.columns
        
        additional_columns: - Indicates whether additional columns may be defined. One of allowed, allowed_if_defined and not_allowed

        initial_columns: - An optional list of columns that must be the first N columns of a file

        index_columns: - An optional list of columns that uniquely identify a row.
        """

        df = pd.DataFrame(columns=initial_columns)
        ds = pa.DataFrameSchema({})
        if index_columns:
            if len(index_columns) == 1:
                index_columns = index_columns[0]
            df.set_index(index_columns, inplace=True)

        return cls()

    def _update_meta(self, columns:dict): ...    

    def _remove_meta(self, columns:list): ...

    def add(self): ...

    def addColumn(self, columnName:str, schema:Column): ...

def stringify_all(orig_df:pd.DataFrame, cols:dict[str, Column]):
    def stringify_lists(cell, delimiter:str):
        """Convert lists into strings using column-specific delimiter."""
        if isinstance(cell, list):
            stringified = delimiter.join(map(str, cell))
            return f"[{stringified}]" 
        return cell

    df = orig_df.copy()
    for col in df.columns:
        cur_col = cols.get(col)
        cur_delim = cur_col.Delimiter
        if cur_delim is not None:
            df[col] = df[col].apply(lambda x: stringify_lists(x, cur_delim))
    
    return df

@define(slots=True)
class tabularFile(DatasetCore):
    
    _schema:ClassVar['Namespace']

    _n_schema_true:int = field(init=False, default=0) #number of times schema has been applied
    data:Union[None, tableView] = field(init=False, default=None)
    _cur_labels:set = field(init=False, factory=set)

    columns:ClassVar[MinimalDict[str, Column]] = HookedDescriptor(columnView,factory=make_column_view,tags="columns")

    def _make_file(self, force:bool):
        final_data = stringify_all(self.data, self.columns)
        """UserDefinedLists have specified delimiters, as such need to convert the lists to strings
        with the delimiter implemented, so that then the correct delimiter in the sublists is used"""
        _write_tsv(self._tree_link.path, final_data, force)

    def _check_schema(self, add_callbacks:bool=False, tags:Union[list,str] = None):

        for flag, label, items in check_schema(self, self._schema, self._cur_labels, add_callbacks, tags):
            if flag == "add":
                self._cur_labels.add(label)
                self._add_metadata_(items)
            elif flag == "del":
                self._cur_labels.remove(label)
                self._remove_metadata_(items)
            else:
                raise RuntimeError(f"unknown flag: {flag} given in {self}._check_schema")
   
    def _add_metadata_(self, items:'Namespace'):
        
        # process columns
        columns = items.get("columns")
        processed_cols = {}
        for key in columns.keys():
            if isinstance(columns[key], str): # the value is a requirement
                processed_cols[key] = Column(key, columns[key])
            else:
                level = columns[key].pop("level")
                met_instance = Column(key, level)
                Column._override[met_instance] = columns[key]
                processed_cols[key] = met_instance

        # get other metadata
        initial_columns = items.get("initial_columns", None) # can be None
        index_columns = items.get("index_columns", None) # can be None
        additional_columns_flag = items.get("additional_columns") # must specify one of allowed, allowed_if_defined, not_allowed
        
        # set table/update
        self._n_schema_true += 1
        if self._n_schema_true > 1:
            if (initial_columns is not None) or (index_columns is not None) or (additional_columns_flag != "n/a"): # check for added columns              
                raise RuntimeError(f"{self.__class__.__name__} can only support one tsv at the moment, please report this error with associated context to reproduce")
            self.data._update_meta(processed_cols)
        else:
            self.data = tableView.create(processed_cols, additional_columns_flag, initial_columns, index_columns)

    def _remove_metadata_(self, items:'Namespace'):
        self._n_schema_true -= 1
        if self._n_schema_true == 0:
            self.data = None
        else:
            keys = items.get("columns").keys()
            self.data._remove_meta(items.get("columns"))

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


class tabularJSONFile(DatasetCore):
    def _check_schema(self, *args, **kwargs):...

    def _make_file(self, force):...
    pass


def _set_tabular_schema(schema:'Namespace'):
    tabularFile._schema = schema.rules.tabular_data
