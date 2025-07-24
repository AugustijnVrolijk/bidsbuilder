from attrs import define, field
from typing import ClassVar, TYPE_CHECKING
from ..core.dataset_core import DatasetCore
from ..schema_objects import Entity, Suffix
from ..core.filenames import CompositeFilename
from ..core.dataset_tree import Directory

from pathlib import Path

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class folderBase(DatasetCore):
    _cur_entity: ClassVar[str] = None

    _val:str = field(repr=True, default=None, alias="_val")

    n:int = field(repr=False, init=False)
    children:list['folderBase'] = field(repr=False, init=False, default=[])

    @property
    def val(self):
        return self._val

    @classmethod
    def create(cls, name, tree:Directory):
        final_entity = Entity(cls._cur_entity, name) # entity format check
        foldername = CompositeFilename(_entities={cls._cur_entity:final_entity})
        instance = cls(_val=final_entity.val)
        tree.add_child(foldername, instance, type_flag="directory")
        return instance

    """
    Keeping val.setter in base class may present problems - duplication of names for sessions and datatypes
    for the subject we can use a classmethod to check all names, but at the moment session and datatype have 
    no variable for their "parent" so can't easily check for duplicate names.

    @val.setter
    def val(self, new_val:str|None):

        self._val = self._check_name(new_val)
        self.foldername.update(self._cur_entity, self._val)
    
    def _check_name(self, new_val:str|None) -> str:
    
        # another thing to consider is whether to allow None Values
        # Specifically without a key to instantiate how would a user later know which numbered folder actually
        # links to their data, defeating the point...
        # possibly if this feature is wanted have a factory method which returns a (instance, ID) tuple to allow 
        # for automation without needing to know foldernames, but keep track of the links between data folders and
        # input data

        if new_val == None:
            new_val = str(self.n)

        assert isinstance(new_val, str), f"Name {new_val} is of type {type(new_val)}, expected str"

        return new_val
    """

    def _make_file(self, force:bool):
        path = Path(self._tree_link.path)
        path.mkdir(parents=False, exist_ok=force)

    def _get_folder_path(self):
        pass

    def __del__(self):
        del self._tree_link # remove reference explicitly, as its referenced as a parent so may be kept
        # if user moves child objects somewhere else

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
        """
        CAN MAKE A MUCH MORE ELEGANT METHOD WHICH DOESN'T STORE CLASS VARIABLES TO CHECK NAME
        INSTEAD JUST USING PARTICIPANTS.TSV TO CHECK IT!!! 
        """
        temp_val = self._check_name(self._val) # check duplicates
        self._val = temp_val # assign once passes both checks

        Subject._n_subjects += 1
        self.n = Subject._n_subjects
        Subject._all_names.add(self._val)

        # --- create subject entity

    @folderBase.val.setter
    def val(self, new_val:str):

        temp_val = self._check_name(new_val) # check for duplicates
        self.foldername.update(self._cur_entity, temp_val) # entity itself checks for format
        
        Subject._all_names.remove(self._val)
        Subject._all_names.add(temp_val) 

    def add_session(self, ses:str=None):
        if ses == None:
            ses = str(len(self.children))

        self._validate_child_name(ses)
        #debated adding a factory creator for session, but doing the following manually in subject
        #would enable the creation of floating sessions, which can be assigned to a subject later
        to_add = Session.create(ses, self._tree_link)

        if self._n_sessions == 0:
            if len(self.children) > 0:
                self._migrate_to_ses(to_add)
        else:
            Subject._pair_session_count += 1 #don't count 1 single session, needs to be 1 or more

        self._n_sessions += 1
        self.children.append(to_add)

        return to_add

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
        
    def add_datatype(self, d_type:str):
        self._validate_child_name(d_type)
        #subject has either got only sessions, or only datatype folders
        if self._n_sessions > 0:
            raise RuntimeError(f"Can't add datatype folder to a subject already containing sessions, please assign it to one of its sessions")
        
        to_add = Datatype(d_type)
        to_add.foldername.parent = self.foldername
        self.children.append(to_add)

    def _check_name(self, new_val:str|None) -> str:

        #new_val = super()._check_name(new_val)
        if new_val in Subject._all_names:
            raise ValueError(f"Duplicate subject val: '{new_val}' for {self}")

        return new_val

    def anonymise(self):
        self.val = str(self.n)

    def __del__(self):
        Subject._n_subjects -= 1
        Subject._all_names.remove(self._val)

        to_inc = max(0, (self._n_sessions - 1)) # use max in case self._n_sessions is 0, in which case it would result in -1
        Subject._pair_session_count -= to_inc
        super().__del__()

@define(slots=True)
class Session(folderBase):
    """
    At the time of writing: 24/06/2025
    Session needs the following context: 

    required:
        - ses_dirs
    """
    def __attrs_post_init__(self):
        # --- create session entity --- Creating the entitiy will validate the the name as well
        #if created from a subject, it will reassign the parent later
        pass

    @classmethod
    def create(cls, name, tree:Directory) -> 'Session':
        final_entity = Entity(cls._cur_entity, name) # entity format check
        foldername = CompositeFilename(_entities={cls._cur_entity:final_entity})
        session = cls(_val=final_entity.val)
        tree.add_child(foldername, session, type_flag="directory")
        return session

    def add_datatype(self, val):
        to_add = Datatype(val)
        to_add.foldername.parent = self.foldername
        self.children.append(Datatype(val))
    
class Datatype(folderBase):

    def __attrs_post_init__(self):
        final_type = Datatype(self._val)
        try:
            is_suffix = Suffix(self._val)
            self.foldername = CompositeFilename(parent=None, datatype=final_type, entities={}, suffix=is_suffix)
        except KeyError as e:
            self.foldername = CompositeFilename(parent=None, datatype=final_type, entities={}, suffix=None)
    
    def add_data(self):
        pass
    
def _set_folder_schemas():
    #schema:'Namespace'
    Session._cur_entity = "session"
    Subject._cur_entity = "subject"
    Datatype._cur_entity = "datatype"

__all__ = ["Subject", "Session"]