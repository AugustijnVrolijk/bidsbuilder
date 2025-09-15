from typing import TYPE_CHECKING, Union, ClassVar, Self
from attrs import define, field
from pathlib import Path
from abc import ABC, abstractmethod
from ...util.hooks import *

if TYPE_CHECKING:
    from ...main_module import BidsDataset
    from .dataset_tree import FileEntry
    from .filenames import filenameBase

@define(slots=True)
class DatasetCore(ABC):
    _dataset:ClassVar["BidsDataset"]
    exists:ClassVar[bool]

    _tree_link: Union['FileEntry', None] = field(repr=True, init=False, default=None, alias="_tree_link")
    _level:str = field(repr=True, default="optional", alias="_level")

    @classmethod
    def create(cls,*, _level:str="optional", exists:bool=True, **kwargs) -> Self:
        if _level == "required":
            exists = True

        obj = cls(_level=_level, **kwargs)
        obj.exists = exists
        return obj

    def __core_post_init__(self, add_callbacks=True):
        """
        Special init once a file object has been initialised with a corresponding name and tree object
        """
        if not self._dataset._frozen:
            self._check_schema(add_callbacks)

    @staticmethod
    def _validate_exists(instance:'DatasetCore', descriptor:'DescriptorProtocol', value:bool) -> bool:
        if not isinstance(value, bool):
            raise TypeError(f"exists must be of type boolean not {type(value)} for {value}") 

        if instance._level == "required":
            return True # must exists for files which are required
        return value

    exists:ClassVar[bool] = HookedDescriptor(bool, default=True, fval=_validate_exists, tags="exists")

    @abstractmethod
    def _check_schema(self, *args, **kwargs):
        ...
    
    @property
    def filename(self) -> 'filenameBase':
        return self._tree_link._name_link

    def _write_BIDS(self, force:bool):
        if self._exists:
            self._make_file(force)

    @abstractmethod
    def _make_file(self, force:bool):
        ...

    def _read_BIDS(self):
        pass

    def delete_self(self):
        return
    
    def __contains__(self, key): #used for selector parsing "in", need it to point it to whatever is needed
        return

class UnknownFile(DatasetCore):
    def _check_schema(self, *args, **kwargs):
        pass
    
    def _make_file(self, force:bool):
        filename = Path(self._tree_link.path)  # or .json, .tsv, etc.
        if self._tree_link.is_dir:
            filename.mkdir(parents=False,exist_ok=force)
        else:
            with open(filename, 'w') as f:
                pass  # creates the file, nothing is written

def _set_dataset_core(dataset:'BidsDataset'):
    DatasetCore._dataset = dataset