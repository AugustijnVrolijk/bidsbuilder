from ..modules.dataset_core import DatasetCore
from ..util.categoryDict import categoryDict

from attrs import define, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..modules.schema_objects import Metadata


@define(slots=True)
class JSONfile(DatasetCore):
    
    _metadata:categoryDict[str, (str, Metadata)] = field(init=False, default=categoryDict())
    _wrong_key:dict = field(init=False, default={}) #for overflow values passed to json which doesn't have a valid key representing it

    @classmethod
    def _create_agnostic_files(cls) -> 'JSONfile':
        pass

    @classmethod
    def _create_data_files(cls) -> 'JSONfile':
        pass

    def _make_file(self):
        pass

    
    def __getattr__(self, name):
        return
    
    def  __setattr__(self, name, value):
        return super().__setattr__(name, value)
    
