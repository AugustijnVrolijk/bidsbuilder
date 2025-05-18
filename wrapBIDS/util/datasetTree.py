"""The below code was taken from src/bids_validator/types/files.py
with a couple modifications for UserDirEntry to point to a datasetCore object
allowing for object retrieval via the fileTree
"""

import os
import attrs
import stat
import posixpath

from attrs import define, field
from typing import Union, TYPE_CHECKING
from pathlib import Path
from functools import cached_property
from typing_extensions import Self
from wrapBIDS.modules.coreModule import DatasetCore


if TYPE_CHECKING:
    from wrapBIDS.bidsDataset import BidsDataset

@define(slots=True)
class UserFileEntry:
    """Partial reimplementation of :class:`os.DirEntry`.

    :class:`os.DirEntry` can't be instantiated from Python, but this can.

    TAKEN FROM src/bids_validator/types/files.py
    """

    #have to add alias otherwise it gets stripped of "_" and gets changed to "name"
    _name: str = field(repr=True, alias="_name")
    link: Union['DatasetCore', 'BidsDataset'] = field(repr=False)
    parent: Union['FileTree', None] = field(repr=False, default=None)

    _stat: os.stat_result = field(init=False, repr=False, default=None)
    _lstat: os.stat_result = field(init=False, repr=False, default=None)


    """
    TODO: ADD A SETTER FOR NAME, IF NAME CHANGES, 
    NEED TO CHANGE THE REFERENCE IN IT'S PARENT,
    I.e update the key to refer to the correct name

    CHECK IF attrs HAS A BETTER WAY OF DOING THIS; ITS POSSIBLE
    THERE IS AN INBUILT FUNCTION WHICH TRIGGERS ON ATTRIBUTE CHANGES
    
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

    def stat(self, *, follow_symlinks: bool = True) -> os.stat_result:
        """Return stat_result object for the entry; cached per entry."""
        if follow_symlinks:
            if self._stat is None:
                self._stat = os.stat(self.path, follow_symlinks=True)
            return self._stat
        else:
            if self._lstat is None:
                self._lstat = os.stat(self.path, follow_symlinks=False)
            return self._lstat

    def is_dir(self, *, follow_symlinks: bool = True) -> bool:
        """Return True if the entry is a directory; cached per entry."""
        _stat = self.stat(follow_symlinks=follow_symlinks)
        return stat.S_ISDIR(_stat.st_mode)

    def is_file(self, *, follow_symlinks: bool = True) -> bool:
        """Return True if the entry is a file; cached per entry."""
        _stat = self.stat(follow_symlinks=follow_symlinks)
        return stat.S_ISREG(_stat.st_mode)

    def is_symlink(self) -> bool:
        """Return True if the entry is a symlink; cached per entry."""
        _stat = self.stat(follow_symlinks=False)
        return stat.S_ISLNK(_stat.st_mode)

    #cannot be @cachedproperty as the name can change in which case the cached version is incorred
    @property
    def relative_path(self) -> str:
        """The path of the current FileTree, relative to the root.

        Follows parents up to the root and joins with POSIX separators (/).
        Directories include trailing slashes for simpler matching.
        """
        if self.parent is None:
            return ''

        return posixpath.join(self.parent.relative_path, self.name)
    
    #cannot be @cachedproperty as the name can change in which case the cached version is incorred
    @property
    def path(self):
        return self.parent.path / self.name

@define(slots=True)
class FileTree(UserFileEntry):
    """Represent a FileTree with cached metadata."""
    #FileTree must be directory
    #UserFileEntry has the required info for dirs and Files

    children: dict[str, 'FileTree'] = field(repr=False, factory=dict)

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
                tClass = FileTree
            else:
                tClass = UserFileEntry
            new_entry = tClass(_name=parts[0], link=obj_ref, parent=self)
            
            self.children[new_entry.name] = new_entry
        else:
            #CURRENT APPROACH WILL NOT BUILD INTERMEDIATE FOLDERS
            try:
                self.children[parts[0]].addPath(posixpath.join(*parts[1:]),obj_ref,is_dir)
            except:
                raise KeyError(f"given path {relpath} refers to an intermediate folder which has not been created")
        
    """NEEDS TO BE REWORKED TO WORK WITH MY CHANGES"""
    @classmethod
    def read_from_filesystem(
        cls,
        direntry: os.PathLike,
        parent: Union['FileTree', None] = None,
    ) -> Self:
        """Read a FileTree from the filesystem.

        Uses :func:`os.scandir` to walk the directory tree.
        """
        self = cls(direntry, parent=parent)
        if self.direntry.is_dir():
            self.is_dir = True
            self.children = {
                entry.name: FileTree.read_from_filesystem(entry, parent=self)
                for entry in os.scandir(self.direntry)
            }
        return self

    def fetch(self, relpath: os.PathLike) -> 'DatasetCore':
        relpath = Path(relpath)
        parts = relpath.parts
        if len(parts) == 0:
            raise ValueError(f"relpath misisng value: {relpath}")
        
        if relpath.root:
            parts = parts[1:]
        
        child = self.children.get(parts[0])

        if len(parts) == 1:
            return child.link
        else:
            return child.fetch(posixpath.join(*parts[1:]))

    def __contains__(self, relpath: os.PathLike) -> bool:
        parts = Path(relpath).parts
        if len(parts) == 0:
            return False
        child = self.children.get(parts[0], False)
        return child and (len(parts) == 1 or posixpath.join(*parts[1:]) in child)

    #cannot be @cachedproperty as the name can change in which case the cached version is incorred
    @property
    def relative_path(self) -> str:
        """The path of the current FileTree, relative to the root.

        Follows parents up to the root and joins with POSIX separators (/).
        Directories include trailing slashes for simpler matching.
        """
        if self.parent is None:
            return ''

        return posixpath.join(self.parent.relative_path,f'{self.name}/')
    
    #cannot be @cachedproperty as the name can change in which case the cached version is incorred
    @property
    def path(self) -> Path:

        if self.parent is None:
            return Path(self.name) 

        return self.parent.path / self.name