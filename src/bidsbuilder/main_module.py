from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from .util.util import checkPath
from .modules.core.dataset_tree import Directory
from .modules.file_bases.directories import Subject
from .schema.schema import parse_load_schema

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace

class BidsDataset():
    """
    At the time of writing: 24/06/2025
    Dataset needs the following context: 

    required:
      - dataset_description
      - tree
      - ignored
      - datatypes
      - modalities
      - subjects
    """
    

    def __init__(self, root:str, minimal:bool=False):
        
        self._frozen = True
        self.root = Path(root).as_posix()
        self.schema:'Namespace' = parse_load_schema()
        self._tree_reference:Directory = Directory(_name=self.root, _file_link=self, _name_link=None, parent=None)
        from .modules import set_all_schema_
        set_all_schema_(self, self.schema)
        from .modules.file_bases.agnostic_files import _make_skeletonBIDS
        _make_skeletonBIDS(self.schema, self.tree, minimal)
        self._frozen = False

    @property
    def _frozen(self):
        return self.__frozen

    @_frozen.setter
    def _frozen(self, val:bool):
        self.__frozen = val
        if val == False:
            for node in self.tree._iter_tree():
                if node._file_link:
                    node._file_link._check_schema(add_callbacks=True)
        elif val != True:
            raise ValueError(f"frozen must be true or false")

    @property
    def tree(self):
        return self._tree_reference

    @property
    def dataset_description(self):
        return self._tree_reference.fetch(r"/dataset_description.json")

    def build(self, force=False):
        #self._removeRedundant() deprecated
        if self.root == None:
            raise FileNotFoundError("Please specify a root directory to build the dataset in")
        """
        exists, msg = checkPath(self.root)
        if not exists:
            raise FileExistsError(msg)
        """
        curGeneratedBy = self.dataset_description["GeneratedBy"]
        generatedby = [{'Name': 'bidsbuilder',
                     'Version': "0.0.1",
                     'Description:': 'Schema-driven pythonic object representation of all BIDS components',
                     'CodeURL': 'https://github.com/AugustijnVrolijk/bidsbuilder',
                     }]
        if curGeneratedBy is None:
            self.dataset_description["GeneratedBy"] = generatedby
        elif isinstance(curGeneratedBy, list):
            self.dataset_description["GeneratedBy"] = curGeneratedBy.append(generatedby)
        else:
            curGeneratedBy = [curGeneratedBy]
            self.dataset_description["GeneratedBy"] = curGeneratedBy.append(generatedby)

        self._tree_reference._make(force)
    
    def _removeRedundant(self):
        for child in self.children:
            if child:
                child._removeRedundant()
            else:
                child._deleteSelf()
                #consider using __del__ method in order to just call pop. Concerns around whether the garbage collection always occurs

                self.children.pop(child)

    def _write_BIDS(self, force:bool):
        path = Path(self.root)
        path.mkdir(parents=False, exist_ok=force)

    def _check_schema(self, *args, **kwargs):
        """placeholder used when tree recursively calls for files to check schema"""
        return

    def read(self, path:str = None):
        if path:
            self.root = path

        exists, msg = checkPath(self.root)
        if not exists():
            raise FileExistsError(msg)

        self.initialised = True
    
    def addSubject(self, name:str) -> Subject:
        sub = Subject.create(name, self.tree)
        return sub