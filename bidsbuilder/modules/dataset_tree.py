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

if TYPE_CHECKING:
    from ..bidsDataset import BidsDataset
    from .dataset_core import DatasetCore
    from .filenames import filenameBase

@define(slots=True)
class FileEntry:
    """Partial reimplementation of :class:`os.DirEntry`.

    :class:`os.DirEntry` can't be instantiated from Python, but this can.

    TAKEN FROM src/bids_validator/types/files.py
    """

    #have to add alias otherwise it gets stripped of "_" and gets changed to "name"
    _name: str = field(repr=True, alias="_name")
    _file_link: Union['DatasetCore', 'BidsDataset'] = field(repr=False)
    _name_link: 'filenameBase' = field(repr=False)
    parent: Union['Directory', None] = field(repr=False, default=None)

    _stat: os.stat_result = field(init=False, repr=False, default=None)
    _lstat: os.stat_result = field(init=False, repr=False, default=None)


    """
    on_setattr (Callable | list[Callable] | None | Literal[attrs.setters.NO_OP]) –
      Allows to overwrite the on_setattr setting from attr.s. If left None, the on_setattr value from attr.s is used. 
      Set to attrs.setters.NO_OP to run no setattr hooks for this attribute – regardless of the setting in define().
    """

    def __attrs_post_init__(self) -> None:
        if isinstance(self.link, DatasetCore):
            #is self.link.name = self.name redundant? Or will I always instantiate it already knowing the instance name
            #self.link.name = self.name
            self.link._tree_reference = self
        return

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
        return str(self.path)

    def fetch_instance(self) -> 'DatasetCore':
        return self.link

    @property
    def relative_path(self) -> str:
        #this method and path may break if FileEntrys can be created without a link to a parent file
        return self.parent.relative_path + self.name
    
    @property
    def path(self) -> str:
        return self.parent.path + self.name

@define(slots=True)
class FileCollection(FileEntry):
    """File collections are stricly not a directory -> They are groups which contain related files
        i.e. A raw data file and it's JSON sidecar file would form a collection, with both individual files being FileEntry's

        This enables grouping of similar metadata between them
    """
    children: dict[str, Union['Directory', 'FileCollection', FileEntry]] = field(repr=False, factory=dict)


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

        return posixpath.join(self.parent.relative_path,f'{self.name}')


@define(slots=True)
class Directory(FileCollection):
    """Represent a directory with its associated files"""
    #UserFileEntry has the required info for dirs and Files

    def addPath(self, raw_path: os.PathLike, obj_ref: 'DatasetCore', is_dir:bool=False):
        
        relpath = Path(raw_path)
        parts = relpath.parts
        if len(parts) == 0:
            raise ValueError(f"relpath misisng value: {relpath}")
        
        #DEPENDS ON SCHEMA SYNTAX, IF A LEADING "/" ALWAYS MEANS ITS AT THE DATASET ROOT WE CAN CHECK THAT PARENT IS NONE
        if relpath.root:
            parts = parts[1:]
    
        if len(parts) == 1:
            if is_dir:
                tClass = Directory
            else:
                tClass = FileEntry
            new_entry = tClass(_name=parts[0], link=obj_ref, parent=self)
            
            self.children[new_entry.name] = new_entry
        else:
            #CURRENT APPROACH WILL NOT BUILD INTERMEDIATE FOLDERS
            try:
                self.children[parts[0]].addPath(posixpath.join(*parts[1:]),obj_ref,is_dir)
            except:
                raise KeyError(f"given path {relpath} refers to an intermediate folder which has not been created")

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
            return Path(self.name) 

        return self.parent.path / self.name