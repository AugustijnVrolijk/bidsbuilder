from typing import TYPE_CHECKING, Union, ClassVar
from attrs import define, field
from pathlib import Path

from ...schema.callback_property import CallbackField

if TYPE_CHECKING:
    from ...main_module import BidsDataset
    from .dataset_tree import FileEntry
    from .filenames import filenameBase

@define(slots=True)
class DatasetCore():
    _dataset:ClassVar["BidsDataset"]
    exists:ClassVar[bool]

    _tree_link: Union['FileEntry', None] = field(repr=True, init=False, default=None, alias="_tree_link")
    _exists:bool = field(repr=True, init=False, default=True, alias="_exists")
    _level:str = field(repr=True, default="optional", alias="_level")

    def __attrs_post_init__(self):
        if self._level == "required":
            self.exists = True

    def __core_post_init__(self, add_callbacks=True):
        """
        Special init once a file object has been initialised with a corresponding name and tree object
        """
        if not self._dataset._frozen:
            self._check_schema(add_callbacks)

    @staticmethod
    def _validate_exists(instance:'DatasetCore', value:bool) -> bool:
        if not isinstance(value, bool):
            raise TypeError(f"exists must be of type boolean not {type(value)} for {value}") 

        if instance._level == "required":
            return True # must exists for files which are required
        return value

    exists:ClassVar[bool] = CallbackField[bool](fval=_validate_exists)

    def _check_schema(self, *args, **kwargs):
        return
        raise NotImplementedError(f"__post_init__ not defined for class {type(self)}")

    @property
    def filename(self) -> 'filenameBase':
        return self._tree_link._name_link

    def _write_BIDS(self, force:bool):
        if self._exists:
            self._make_file(force)

    def _make_file(self, force:bool):
        filename = Path(self._tree_link.path)  # or .json, .tsv, etc.
        if self._tree_link.is_dir:
            filename.mkdir(parents=False,exist_ok=force)
        else:
            with open(filename, 'w') as f:
                pass  # creates the file, nothing is written
        #raise NotImplementedError(f"no _make_file defined for {self}")

    def _read_BIDS(self):
        pass

    def deleteSelf(self):
        return
    
    def __contains__(self, key): #used for selector parsing "in", need it to point it to whatever is needed
        return

def _set_dataset_core(dataset:'BidsDataset'):
    DatasetCore._dataset = dataset