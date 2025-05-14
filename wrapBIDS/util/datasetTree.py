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

if TYPE_CHECKING:
    from wrapBIDS.modules.coreModule import DatasetCore
    from wrapBIDS.bidsDataset import BidsDataset

@define
class UserFileEntry:
    """Partial reimplementation of :class:`os.DirEntry`.

    :class:`os.DirEntry` can't be instantiated from Python, but this can.
    """

    path: str = field(repr=False, converter=os.fspath)
    name: str = field(init=False)
    link: Union['DatasetCore', 'BidsDataset'] = field(repr=False)
    is_dir: bool = field(repr=False, default=False)
    parent: Union['FileTree', None] = field(repr=False, default=None)

    _stat: os.stat_result = field(init=False, repr=False, default=None)
    _lstat: os.stat_result = field(init=False, repr=False, default=None)

    def __attrs_post_init__(self) -> None:
        self.name = os.path.basename(self.path)

    def __fspath__(self) -> str:
        return self.path

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

    def relative_path(self) -> str:
        """The path of the current FileTree, relative to the root.

        Follows parents up to the root and joins with POSIX separators (/).
        Directories include trailing slashes for simpler matching.
        """
        if self.parent is None:
            return ''

        return posixpath.join(self.parent.relative_path, self.name)
    
@define
class FileTree(UserFileEntry):
    """Represent a FileTree with cached metadata."""
    #FileTree must be directory
    #UserFileEntry has the required info for dirs and Files

    children: dict[str, 'FileTree'] = field(repr=False, factory=dict)

    def addPath(self, relpath: os.PathLike, obj_ref: 'DatasetCore', is_dir:bool=False):
        
        """ADD A CHECK IN CASE INTERMEDIATE FOLDERS NEED TO BE MADE, I.E. Relpath given is for a session folder
        so the subject folder needs to be made"""

        if is_dir:
            tClass = FileTree
        else:
            tClass = UserFileEntry
        new_entry = tClass(path=relpath, link=obj_ref, parent=self, is_dir=is_dir)
        
        self.children[new_entry.name] = new_entry
    
    
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

    def __contains__(self, relpath: os.PathLike) -> bool:
        parts = Path(relpath).parts
        if len(parts) == 0:
            return False
        child = self.children.get(parts[0], False)
        return child and (len(parts) == 1 or posixpath.join(*parts[1:]) in child)

    @cached_property
    def relative_path(self) -> str:
        """The path of the current FileTree, relative to the root.

        Follows parents up to the root and joins with POSIX separators (/).
        Directories include trailing slashes for simpler matching.
        """
        if self.parent is None:
            return ''

        return posixpath.join(self.parent.relative_path,f'{self.name}/')
    