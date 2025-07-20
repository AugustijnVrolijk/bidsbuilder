from typing import TYPE_CHECKING, Union, ClassVar
from attrs import define, field

if TYPE_CHECKING:
    from ..bidsDataset import BidsDataset
    from .dataset_tree import FileEntry
    from .filenames import filenameBase

@define(slots=True)
class DatasetCore():
    _dataset:ClassVar["BidsDataset"]

    _tree_link: Union['FileEntry', None] = field(repr=True, init=False, default=None, alias="_tree_link")
    _exists:bool = field(repr=True, init=False, default=True, alias="_exists")
    _level:str = field(repr=True, default="optional", alias="_level")

    def __attrs_post_init__(self):
        if self._level == "required":
            self.exists = True

    def __post_init__(self):
        #not from attrs, but if an init needs to be run, once filename and the tree reference have been linked
        pass

    @property 
    def exists(self):
        return self._exists
    
    @exists.setter
    def exists(self, value):
        if not isinstance(value, bool):
            raise TypeError(f"exists must be of type boolean not {type(value)} for {value}") 

        if self._level != "required":
            self._exists = value

    @property
    def filename(self):
        return self._tree_link._file_link

    def _write_BIDS(self, force:bool):
        if self._exists:
            self._make_file(force)

    def _make_file(self, force:bool):
        pass
        #raise NotImplementedError(f"no _make_file defined for {self}")

    def _read_BIDS(self):
        pass

    def deleteSelf(self):
        return
    
    def __contains__(self, key): #used for selector parsing "in", need it to point it to whatever is needed
        return


def _set_dataset_core(dataset:'BidsDataset'):
    DatasetCore._dataset = dataset