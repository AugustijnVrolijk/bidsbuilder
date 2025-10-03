from __future__ import annotations

import pandas as pd
import pandera.pandas as pa
from pandas.api.types import infer_dtype
from attrs import define, field
from typing import TYPE_CHECKING, ClassVar, Any, Union, Generator, Self

from ...util.io import _write_json, _write_tsv
from ..core.dataset_core import DatasetCore
from ...util.hooks import *
from ..schema_objects import Column, UserDefinedColumn
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

ALLOWED = 2
ALLOWED_IF_DEFINED = 1
NOT_ALLOWED = 0

@define(slots=True)
class tableView():
    
    data:pd.DataFrame = field() # at the moment will not 
    data_schema:pa.DataFrameSchema = field() # validator to check input data
    #index_columns:set = field() # 
    additional_columns_flag = field() # allowed, allowed_if_defined, not_allowed
    columns:dict = field()

    @classmethod
    def _create(cls, columns:dict[str, Column], additional_columns_flag:str, initial_columns:list=None, index_columns:list=None) -> Self:
        """
        columns: - dict with values that may be found in objects.columns
        
        additional_columns: - Indicates whether additional columns may be defined. One of allowed, allowed_if_defined and not_allowed

        initial_columns: - An optional list of columns that must be the first N columns of a file

        index_columns: - An optional list of columns that uniquely identify a row.
        """
        flag_converter = {
            "allowed":ALLOWED,
            "allowed_if_defined":ALLOWED_IF_DEFINED,
            "not_allowed":NOT_ALLOWED
        }

        # get validator flag
        flag_val = flag_converter.get(additional_columns_flag)
        if flag_val is None:
            raise ValueError(f"additional columns flag {additional_columns_flag} is not recognised. Must be one of {flag_converter.keys()}")

        # create original dataframe
        df = pd.DataFrame(columns=initial_columns)
        if index_columns:
            if len(index_columns) == 1:
                index_columns = index_columns[0]
            df.set_index(index_columns, inplace=True)
        
        #create dataschema checker
        check_data = {}
        for key, val in columns.items():
            check_data[key] = pa.Column(int, pa.Check(lambda s: val.val_checker(s)))
        ds = pa.DataFrameSchema(check_data)

        return cls(data=df, data_schema=ds, additional_columns_flag=flag_val, columns=columns)

    def _update_meta(self, columns:dict):  
        self.columns.update(columns)
        self.data_schema.add_columns(columns)

    def _remove_meta(self, columns:list):
        for col in columns:
            del self.columns[col]
        self.data_schema.remove_columns(columns)
        raise NotImplementedError("NEED TO ACTUALLY REMOVE DATAFRAME COLUMNS")

    def _merge_validated(self, candidate: pd.DataFrame):
        """
        Internal method:
        - Validates candidate dataframe against schema.
        - Updates existing rows and appends new rows.
        """
        # enforce schema
        candidate = self.data_schema.validate(candidate)

        # updates: overlap in index
        updates = candidate.loc[candidate.index.isin(self.data.index)]
        if not updates.empty:
            self.data.update(updates)

        # new rows: not already in self.data
        new_rows = candidate.loc[~candidate.index.isin(self.data.index)]
        if not new_rows.empty:
            self.data = pd.concat([self.data, new_rows])

        return self

    def addDataframe(self, df: pd.DataFrame):
   
        extra = set(df.columns) - set(self.columns.keys())
        if extra:
            raise ValueError(f"Column mismatch between giving dataframe and existing dataframe. Please first addColumn to resolve")

        return self._merge_validated(df)

    def addRow(self, values: dict):
        """
        Add a single row (requires primary key).
        """
        df = pd.DataFrame([values])
        if self.data.index.name:
            df.set_index(self.data.index.name, inplace=True)

        if df.index.isin(self.data.index).any():
            raise ValueError(f"Primary key {df.index.tolist()} already exists.")

        return self._merge_validated(df)

    def addValues(self, pk, values: dict):
        """
        Update values for a given primary key.
        """
        if pk not in self.data.index:
            raise KeyError(f"Primary key {pk} not found.")

        candidate = self.data.loc[[pk]].copy()
        for col, val in values.items():
            candidate.at[pk, col] = val

        return self._merge_validated(candidate)

    def delRow(self, pk):
        """
        Remove a row by primary key.
        No validation is performed.
        """
        if pk not in self.data.index:
            raise KeyError(f"Primary key {pk} not found.")
        self.data.drop(pk, inplace=True)
        return self

    def delValues(self, pk, columns: list[str]):
        """
        Set specified columns in a row to NA/null.
        No validation is performed (handled downstream).
        """
        if pk not in self.data.index:
            raise KeyError(f"Primary key {pk} not found.")

        for col in columns:
            if col not in self.data.columns:
                raise KeyError(f"Column {col} not found.")
            self.data.at[pk, col] = pd.NA

        return self

    def addColumn(self, columnName:str, schema:Union[Column, dict]=None):
        if self.additional_columns_flag == NOT_ALLOWED:
            raise TypeError(f"Tabular file {self} does not allow adding columns")
        elif self.additional_columns_flag == ALLOWED_IF_DEFINED:
            if columnName not in self.columns:
                raise TypeError(f"Tabular file {self} only allows adding one of the following columns {self.columns.keys()}")
            raise NotImplementedError("NEED TO ADD COLUMN HERE")
        else:
            if isinstance(schema, dict):
                schema = UserDefinedColumn.create(name=columnName, **schema)
            raise NotImplementedError("NEED TO ADD COLUMN HERE")

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
                raise RuntimeError(f"{self.__class__.__name__} cannot support the additional given tsv at the moment, please report this error with associated context to reproduce")
            self.data._update_meta(processed_cols)
        else:
            self.data = tableView._create(processed_cols, additional_columns_flag, initial_columns, index_columns)

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
