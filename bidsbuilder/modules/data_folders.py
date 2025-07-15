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
    children:list['folderBase'] = field(repr=False, init=False, default=[])
    foldername: CompositeFilename = field(init=False, repr=False)

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
    _n_subjects: ClassVar[int] = 0 #to anonymise / give label if no name is given
    _all_names: ClassVar[set[str]] = set() #ensure no duplicate names are given
    _pair_session_count: ClassVar[int] = 0 #if 0, will omit creating the session subdir

    _n_sessions:int = field(default=0, init=False, repr=False)

    def __attrs_post_init__(self):
        # --- checking valid val ---
        Subject._n_subjects += 1
        self.n = Subject._n_subjects
        self._val = self._check_name(self._val)
        Subject._all_names.add(self._val)

        # --- create subject entity
        final_entity = Entity(self._cur_entity, self._val)
        self.foldername = CompositeFilename(parent=None, entities={self._cur_entity:final_entity}, suffix=None)

    @folderBase.val.setter
    def val(self, new_val:str|None):

        Subject._all_names.remove(self._val)
        super().val = new_val
        Subject._all_names.add(self._val)

    def addSession(self, ses:str=None):
        if ses == None:
            ses = str(len(self.children))

        self._validate_child_name(ses)
        #debated adding a factory creator for session, but doing the following manually in subject
        #would enable the creation of floating sessions, which can be assigned to a subject later
        to_add = Session(ses)
        to_add.foldername.parent = self.foldername

        if self._n_sessions == 0:
            if len(self.children) > 0:
                self._migrate_to_ses(to_add)
        else:
            self._pair_session_count += 1 #don't count 1 single session, needs to be 1 or more

        self._n_sessions += 1

    def _migrate_to_ses(self, ses_parent:'Session'):

        #include new session to correctly ID children
        for child in self.children:
            assert isinstance(child, Datatype), f"Failed to migrate {self}'s subfolders to session dir, expected {child} to be of type: Datatype"
            child.foldername.parent = ses_parent.foldername
        
        #reset children
        ses_parent.children = self.children
        self.children = [ses_parent]

    def _validate_child_name(self, new_name):
        for child in self.children:
            assert child.val != new_name, f"Cannot add folder {new_name} with duplicate names/type for {self}"
            
    def addDatatype(self, d_type:str):
        pass

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
    def __attrs_post_init__(self):
        # --- create session entity
        final_entity = Entity(self._cur_entity, self._val)
        #if created from a subject, it will reassign the parent later
        self.foldername = CompositeFilename(parent=None, entities={self._cur_entity:final_entity}, suffix=None)
        
    def add(self, val):
        self.children.append(Datatype(val))

        pass
    
class Datatype(folderBase):

    def __attrs_post_init__(self):
        final_type = Datatype(self._val)
        try:
            is_suffix = Suffix(self._val)
            self.foldername = CompositeFilename(parent=None, datatype=final_type, entities={}, suffix=is_suffix)
        except KeyError as e:
            self.foldername = CompositeFilename(parent=None, datatype=final_type, entities={}, suffix=None)
    
    def _check_name(self, new_val:str) -> str:
        #datatype cannot be an int, so don't have check for None type from folderBase which converts to n
        assert isinstance(new_val, str), f"Name {new_val} is of type {type(new_val)}, expected str"
        
        return new_val
    pass
    
def _set_folder_dataset_ref(dataset:'BidsDataset'):
    Subject.dataset = dataset

def _set_folder_schemas():
    #schema:'Namespace'
    Session._cur_entity = "session"
    Subject._cur_entity = "subject"
    Datatype._cur_entity = "datatype"

__all__ = ["Subject", "Session"]