from attrs import define, field
from typing import ClassVar, TYPE_CHECKING

from ..modules.schema_objects import CompositeFilename, Entity, Suffix

if TYPE_CHECKING:
    from ..bidsDataset import BidsDataset
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class folderBase():
    _cur_entity: ClassVar[str] = None
    dataset: ClassVar['BidsDataset'] = None

    _val:str = field(repr=True, default=None, alias="_val")

    n:int = field(repr=False, init=False)
    children:list = field(repr=False, init=False, default=[])
    foldername: CompositeFilename = field(init=False, repr=False)

    def __attrs_post_init__(self):
        final_entity = Entity(self._cur_entity, self._val)
        self.foldername = CompositeFilename(parent=None, entities={self._cur_entity:final_entity}, suffix=None)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, new_val:str|None):

        self._val = self._check_name(new_val)
        self.foldername.update(self._cur_entity, self._val)
    
    def _check_name(self, new_val:str|None) -> str:
        if new_val == None:
            new_val = str(self.n)

        assert isinstance(new_val, str), f"Name {new_val} is of type {type(new_val)}, expected str"

        return new_val

@define(slots=True)
class Subject(folderBase):
    """
    At the time of writing: 24/06/2025
    Subject needs the following context: 

    required:
      - sessions
    """
    _n_subjects: ClassVar[int] = 0
    _all_names: ClassVar[set[str]] = set()
    
    def __attrs_post_init__(self):
        # --- checking valid val ---
        Subject._n_subjects += 1
        self.n = Subject._n_subjects
        self._val = self._check_name(self._val)
        Subject._all_names.add(self._val)

        # --- create subject entity
        sub_entity = Entity("subject", self._val)
        self.foldername = CompositeFilename(parent=None, entities={"subject":sub_entity}, suffix=None)

    @folderBase.val.setter
    def val(self, new_val:str|None):

        Subject._all_names.remove(self._val)
        super().val = new_val
        Subject._all_names.add(self._val)

    def _check_name(self, new_val:str|None) -> str:

        new_val = super()._check_name(new_val)
        if new_val in Subject._all_names:
            raise ValueError(f"Duplicate subject val: '{new_val}' for {self}")

        return new_val

    def anonymise(self):
        self.val = str(self.n) 

@define(slots=True)
class Session(folderBase):
    """
    At the time of writing: 24/06/2025
    Session needs the following context: 

    required:
        - ses_dirs
    """

class Datatype(folderBase):

    def __attrs_post_init__(self):
        final_type = Datatype(self._val)
        try:
            is_suffix = Suffix(self._val)
            self.foldername = CompositeFilename(parent=None, datatype=final_type, entities={}, suffix=is_suffix)
        except KeyError as e:
            self.foldername = CompositeFilename(parent=None, datatype=final_type, entities={}, suffix=None)


    @property
    def val(self):
        return self._val

    @folderBase.val.setter
    def val(self, new_val:str|None):

        self._val = self._check_name(new_val)
        self.foldername.update(self._cur_entity, self._val)
    
    def _check_name(self, new_val:str|None) -> str:
        if new_val == None:
            new_val = str(self.n)

        assert isinstance(new_val, str), f"Name {new_val} is of type {type(new_val)}, expected str"

        return new_val
    pass
    
def _set_folder_schemas():
    #schema:'Namespace'
    Session._cur_entity = "session"
    Subject._cur_entity = "subject"
    Datatype._cur_entity = "datatype"

__all__ = ["Subject", "Session"]