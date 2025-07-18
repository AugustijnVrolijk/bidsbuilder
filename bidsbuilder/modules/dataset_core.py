from typing import TYPE_CHECKING, Union, ClassVar
from attrs import define, field

if TYPE_CHECKING:
    from ..bidsDataset import BidsDataset
    from .dataset_tree import FileEntry
    from .filenames import filenameBase

@define(slots=True)
class DatasetCore():
    _dataset:ClassVar["BidsDataset"] = None

    _tree_link: Union['FileEntry', None] = field(repr=False, init=False, default=None)
    _exists:bool = field(repr=False,init=False,default=True)

    def __init__(self, path:str, **kwargs):
        self._name:str = path
        
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, val:str):
        if not self._tree_link is None:
            self._tree_link.name = val
        self._name = val
        return 
    
    @property 
    def exists(self):
        return self._exists
    
    @exists.setter
    def exists(self, value):
        assert isinstance(value, bool), f"property exists for {self} must be True or False"
        self.exists = value

    def _write_BIDS(self):
        pass

    def _read_BIDS(self):
        pass

    def deleteSelf(self):
        return
    
    def __contains__(self, key): #used for selector parsing "in", need it to point it to whatever is needed
        return

def _set_dataset_core(dataset:'BidsDataset'):
    DatasetCore.dataset = dataset