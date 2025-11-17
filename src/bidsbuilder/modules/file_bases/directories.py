from __future__ import annotations

from attrs import define, field
from typing import ClassVar, TYPE_CHECKING, Self
from ..core.dataset_core import DatasetCore
from ..schema_objects import Entity, Suffix
from ..core.filenames import CompositeFilename
from ..core.dataset_tree import Directory

from pathlib import Path

if TYPE_CHECKING:
    from .directories import folderBase
    from .tabular_files import tabularFile

@define(slots=True)
class folderBase(DatasetCore):
    _cur_entity: ClassVar[str] = (None, None)

    n:int = field(repr=False, init=False)
    children:list['folderBase'] = field(repr=False, init=False, factory=list)

    @classmethod
    def create(cls, name, tree:Directory):
        """
        safe way of instantiating a folderbase object and linking it to the dataset tree - Used for subject, session and datatype
        """
        # create method links the tree object, to this folderBase object to the filenameObject
        foldername = CompositeFilename.create(entities={cls._cur_entity[0]:(cls._cur_entity[1], name)})
        instance = cls()
        tree.add_child(foldername, instance, type_flag="directory")
        return instance

    """
    Keeping val.setter in base class may present problems - duplication of names for sessions and datatypes
    for the subject we can use a classmethod to check all names, but at the moment session and datatype have 
    no variable for their "parent" so can't easily check for duplicate names.

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
    def _check_schema(self, *args, **kwargs):
        """
        Consider adding specifics in Subject, Session.

        I.e. link it to create the subject or session related folders, i.e. scans.tsv etc..
        
        """
        ...

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
    _n_subjects: ClassVar[int] = 0 # to anonymise / give label if no name is given
    _pair_session_count: ClassVar[int] = 0 # if 0, will omit creating the session subdir

    _n_sessions:int = field(default=0, init=False, repr=False)

    @property
    def val(self) -> str:
        return self._tree_link._name_link.entities[self._cur_entity[0]].val

    def __core_post_init__(self):
        # --- checking valid val ---
        
        self._check_name(self.val) # check duplicates
        self.participants.addRow(f"sub-{self.val}")
        Subject._n_subjects += 1
        self.n = Subject._n_subjects
        super().__core_post_init__()

    @property
    def participants(self) -> 'tabularFile':
        return self._dataset.tree.fetch(r"/participants.tsv")

    @val.setter
    def val(self, new_val:str):

        new_val = self._check_name(new_val) # check for duplicates
        self.participants.delRow(f"sub-{self.val}")
        self.participants.addRow(f"sub-{new_val}")
        self._tree_link._name_link.update_entity(self._cur_entity[0], new_val) # entity itself checks for format


    def add_session(self, ses:str=None):
        if ses == None:
            ses = str(len(self.children))

        self._validate_child_name(ses)
        #debated adding a factory creator for session, but doing the following manually in subject
        #would enable the creation of floating sessions, which can be assigned to a subject later
        to_add = Session.create(ses, self._tree_link)

        # check if we need to migrate existing datatype folders to session folder
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
            if not isinstance(child, Datatype):
                raise TypeError(f"Failed to migrate {self}'s subfolders to session dir, expected {child} to be of type: Datatype")
            child._tree_link.parent = ses_parent._tree_link

        #reset children
        ses_parent.children = self.children
        self.children = [ses_parent]

    def _validate_child_name(self, new_name):
        for child in self.children:
            if child.val == new_name:
                raise ValueError(f"Cannot add folder {new_name} with duplicate names/type for {self}")
        
    def add_datatype(self, d_type:str):
        self._validate_child_name(d_type)
        #subject has either got only sessions, or only datatype folders
        if self._n_sessions > 0:
            raise RuntimeError(f"Can't add datatype folder to a subject already containing sessions, please assign it to one of its sessions")
        
        to_add = Datatype.create(d_type)
        self.children.append(to_add)

    def _check_name(self, new_val:str|None) -> str:

        participant_key = f"sub-{new_val}"
        if self.participants.isRow(participant_key):
            raise ValueError(f"Duplicate subject val: '{new_val}' for {self}, already exists in dataset")
        
        return new_val

    def anonymise(self):
        self.val = str(self.n)

    def __del__(self):
        # have to be careful with anonymise here, when _n_subjects decrements it could lead to different subjects getting the same
        # n label. Need a better system to manage this... i.e. decrement all n values above this one? -> need a store of the subjects
        Subject._n_subjects -= 1

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
    @property
    def val(self) -> str:
        return self._tree_link._name_link.entities[self._cur_entity[0]].val

    @val.setter
    def val(self, new_val:str):
        new_val = self._validate_child_name(new_val) # check for duplicates
        self._tree_link._name_link.update_entity(self._cur_entity[0], new_val) # entity itself checks for format

    def _validate_child_name(self, new_name):
        for child in self.children:
            if child.val == new_name:
                raise ValueError(f"Cannot add folder {new_name} with duplicate names/type for {self}")
        
    def add_datatype(self, d_type:str):
        self._validate_child_name(d_type)
        #subject has either got only sessions, or only datatype folders
        to_add = Datatype.create(d_type)
        self.children.append(to_add)
    
class Datatype(folderBase):

    @classmethod
    def create(cls, name, tree:Directory):
        """
        safe way of instantiating a folderbase object and linking it to the dataset tree
        """
        # check if suffix == 
        try:
            Suffix(name)
            is_suffix = True
        except KeyError as e:
            is_suffix = False

        kwargs = {"datatype":name}
        if is_suffix:
            kwargs["suffix"] = name

        foldername = CompositeFilename.create(**kwargs)
        instance = cls()
        tree.add_child(foldername, instance, type_flag="directory")
        return instance

    @property
    def val(self) -> str:
        return self._tree_link._name_link.datatype

    @val.setter
    def val(self, new_val:str):
        new_val = self._validate_child_name(new_val) # check for duplicates

        self._tree_link._name_link.datatype = new_val # datatype itself checks for format
        try:
            Suffix(new_val)
            is_suffix = True
        except KeyError as e:
            is_suffix = False
        if is_suffix:
            self._tree_link._name_link.suffix = new_val


    def add_data(self):
        pass
    
def _set_folder_schemas():
    #schema:'Namespace'
    Session._cur_entity = ("session", "recommended")
    Subject._cur_entity = ("subject", "required")
    Datatype._cur_entity = ("datatype", "required")

__all__ = ["Subject", "Session"]