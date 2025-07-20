"""The below code was taken from src/bids_validator/types/files.py
with a couple modifications for UserDirEntry to point to a datasetCore object
allowing for object retrieval via the fileTree
"""

import os
import stat
import posixpath

from attrs import define, field
from typing import Union, TYPE_CHECKING
from pathlib import Path
from .filenames import filenameBase
from .dataset_core import DatasetCore

if TYPE_CHECKING:
    from ..bidsDataset import BidsDataset

@define(slots=True)
class FileEntry:
    """Partial reimplementation of :class:`os.DirEntry`.

    :class:`os.DirEntry` can't be instantiated from Python, but this can.

    TAKEN FROM src/bids_validator/types/files.py
    """

    #have to add alias otherwise it gets stripped of "_" and gets changed to "name"
    _name: str = field(repr=True, alias="_name")
    _file_link: Union['DatasetCore', 'BidsDataset'] = field(repr=False, alias='_file_link')
    _name_link: 'filenameBase' = field(repr=False, alias='_name_link')
    parent: Union['Directory', None] = field(repr=False, default=None)

    _stat: os.stat_result = field(init=False, repr=False, default=None)
    _lstat: os.stat_result = field(init=False, repr=False, default=None)


    """
    on_setattr (Callable | list[Callable] | None | Literal[attrs.setters.NO_OP]) –
    Allows to overwrite the on_setattr setting from attr.s. If left None, the on_setattr value from attr.s is used. 
    Set to attrs.setters.NO_OP to run no setattr hooks for this attribute – regardless of the setting in define().
    """

    def __attrs_post_init__(self) -> None:
        
        fully_init = 0

        if isinstance(self._file_link, DatasetCore):
            #is self.link.name = self.name redundant? Or will I always instantiate it already knowing the instance name
            self._file_link._tree_link = self
            fully_init += 1

        if isinstance(self._name_link, filenameBase):
            self._name_link._tree_link = self
            fully_init += 1

        if fully_init == 2:
            self._file_link.__post_init__()
        
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, new_name:str):
        if new_name in self.parent.children.keys():
            raise KeyError(f"key {new_name} already exists in {self.parent}")
        
        #add new entry to parent dict
        self.parent.children[new_name] = self
        #remove old
        self.parent.children.pop(self.name)
        self._name = new_name

    def __fspath__(self) -> str:
        return self.path

    def fetch_instance(self) -> 'DatasetCore':
        return self._file_link

    @property
    def relative_path(self) -> str:
        #this method and path may break if FileEntrys can be created without a link to a parent file
        return self.parent.relative_path + self.name
    
    @property
    def path(self) -> str:
        return self.parent.path + self.name

    def _make(self, force:bool):
        self._file_link._write_BIDS(force)

@define(slots=True)
class FileCollection(FileEntry):
    """File collections are stricly not a directory -> They are groups which contain related files
        i.e. A raw data file and it's JSON sidecar file would form a collection, with both individual files being FileEntry's

        This enables grouping of similar metadata between them
    """
    children: dict[str, Union['Directory', 'FileCollection', 'FileEntry']] = field(repr=False, factory=dict)

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()

    def add_tree_node(self, name_ref: 'FileEntry'):
        assert type(name_ref) == FileEntry, 'Collection add_tree_node expects strictly a FileEntry'
        self.children[name_ref.name] = name_ref

    def add_child(self, name_ref: 'filenameBase', file_ref: 'DatasetCore') -> 'FileEntry':
        
        relpath:Path = Path(name_ref.name)
        parts = relpath.parts
        if relpath.root:
            parts = parts[1:]
        assert len(parts) == 1, f"given file {name_ref} has no name"
        #DEPENDS ON SCHEMA SYNTAX, IF A LEADING "/" ALWAYS MEANS ITS AT THE DATASET ROOT WE CAN CHECK THAT PARENT IS NONE
        

        #file collections can only add fileEntrys
        new_entry = FileEntry(_name=parts[0], _file_link=file_ref, _name_link=name_ref, parent=self)
        self.children[parts[0]] = new_entry
        return new_entry

    def fetch(self, relpath: str, reference:bool=True) -> Union[None, 'DatasetCore', FileEntry]:
        #reference tells whether to return the UserFileEntry|FileTree instance or its linked DatasetCore instance 
        
        relpath = str(relpath)
        assert relpath.startswith(self.name), f"{relpath} is not a child of {self} - {self.name}"

        child_name = relpath[len(self.name):]
        child = self.children.get(child_name)
        if child is None:
            return None
        
        if reference:
            return child.fetch_instance()
        return child

    @property
    def relative_path(self) -> str:
        """The path of the current FileTree, relative to the root.

        Follows parents up to the root and joins with POSIX separators (/).
        Directories include trailing slashes for simpler matching.
        """
        if self.parent is None: #not root dir, relative path includes it
            return self.name

        return posixpath.join(self.parent.relative_path,f'{self.name}') 
    
    @property
    def path(self) -> str:

        if self.parent is None:
            return self.name 

        return posixpath.join(self.parent.path,f'{self.name}')

    def _make(self, force:bool):
        for child in self.children.values():
            child._make(force)

@define(slots=True)
class Directory(FileCollection):
    """Represent a directory with its associated files"""
    #UserFileEntry has the required info for dirs and Files

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()

    def add_tree_node(self, name_ref: Union['Directory', 'FileCollection', 'FileEntry']):
        assert isinstance(name_ref, FileEntry), 'Directory add_tree_node expects a FileEntry or subclass'
        self.children[name_ref.name] = name_ref
        name_ref.parent = self

    def add_child(self, name_ref: 'filenameBase', file_ref: 'DatasetCore', type_flag:str='collection') -> Union['Directory','FileCollection','FileEntry']:

        child_type = {
            "collection": FileCollection,
            "directory": Directory,
            "file": FileEntry
        }
        ret_class:FileEntry = child_type[type_flag.lower()]
        
        relpath:Path = Path(name_ref.name)
        parts = relpath.parts
        if relpath.root:
            parts = parts[1:]
        assert len(parts) == 1, f"given file {name_ref} has no name"
        
        new_entry = ret_class(_name=parts[0], _file_link=file_ref, _name_link=name_ref, parent=self)
        self.children[parts[0]] = new_entry
        
        return new_entry
        """
        #CURRENT APPROACH WILL NOT BUILD INTERMEDIATE FOLDERS
            try:
                self.children[parts[0]].addPath(posixpath.join(*parts[1:]),obj_ref,is_dir)
            except:
                raise KeyError(f"given path {relpath} refers to an intermediate folder which has not been created")
        """

    def fetch(self, relpath: os.PathLike, reference:bool=True) -> Union[None, 'DatasetCore', FileEntry]:
        #reference tells whether to return the UserFileEntry|FileTree instance or its linked DatasetCore instance 

        relpath = Path(relpath)
        parts = relpath.parts
        if len(parts) == 0:
            raise ValueError(f"relpath missing value: {relpath}")
        
        #remove the "\\" or "/" from path parts
        if relpath.root:
            parts = parts[1:]
        
        child = self.children.get(parts[0])
        if child is None:
            return None
        
        if len(parts) == 1:
            if reference:
                return child.link
            return child
        return child.fetch(posixpath.join(*parts[1:]), reference)

    def __contains__(self, relpath: os.PathLike) -> bool:
        parts = Path(relpath).parts
        if len(parts) == 0:
            return False
        child = self.children.get(parts[0], False)
        return child and (len(parts) == 1 or posixpath.join(*parts[1:]) in child)

    @property
    def relative_path(self) -> str:
        """The path of the current Dir, relative to the root.

        Follows parents up to the root and joins with POSIX separators (/).
        Directories include trailing slashes for simpler matching.
        """
        if self.parent is None: #root dir
            return '/'

        return posixpath.join(self.parent.relative_path,f'{self.name}/')
    
    @property
    def path(self) -> str:

        if self.parent is None:
            return f"{self.name}/"   #need to add the trailing / as fileEntry just does parent.path + self.name
        #so without the trailing / it would skip the / between the file and directory. 
        #this is necessary to enable collections to work as containers but not directories

        return posixpath.join(self.parent.path,f'{self.name}/')

    def _make(self, force:bool):
        self._file_link._write_BIDS(force)
        for child in self.children.values():
            child._make(force)