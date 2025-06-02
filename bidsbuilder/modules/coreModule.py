from typing import TYPE_CHECKING, Union
from bidsbuilder.util.categoryDict import catDict

import attrs

if TYPE_CHECKING:
    from bidsbuilder.bidsDataset import BidsDataset
    from bidsbuilder.util.datasetTree import UserFileEntry
    #from wrapBIDS.util.datasetTree import UserFileEntry

class DatasetCore():
    dataset:"BidsDataset" = None

    def __init__(self, path:str, **kwargs):
        self._name:str = path
        self._exists:bool = False
        self.level:str = kwargs.pop("level", "optional")
        if self.level == "required":
            self._exists = True
        self._tree_reference:Union['UserFileEntry'|None] = None

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, val:str):
        if not self._tree_reference is None:
            self._tree_reference.name = val
        self._name = val
        return 
    
    @property 
    def exists(self):
        return self._exists
    
    @exists.setter
    def exists(self, value):
        if not isinstance(value, bool):
            raise TypeError(f"exists must be of type boolean not {type(value)} for {value}") 

        if self.level != "required":
            self._exists = value

    def _write_BIDS(self):
        pass

    def _read_BIDS(self):
        pass

    def deleteSelf(self):
        return
    
    def __contains__(self, key): #used for selector parsing "in", need it to point it to whatever is needed
        return

