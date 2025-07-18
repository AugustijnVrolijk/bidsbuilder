from pathlib import Path
from typing import TYPE_CHECKING
from .util.util import checkPath
from .modules.dataset_tree import Directory
from .util.schema import parse_load_schema

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
    initialised = False
    
    def __init__(self, root:str = Path.cwd()):
        

        self.root = root
        self.schema:'Namespace' = parse_load_schema()
        self._tree_reference:Directory = Directory(_name=root, link=self, parent=None)
        from .modules import set_all_schema_
        set_all_schema_(self, self.schema)
        from .modules.agnostic_files import _make_skeletonBIDS
        _make_skeletonBIDS()
        
    @property
    def tree(self):
        return self._tree_reference

    @property
    def dataset_description(self):
        return self._tree_reference.fetch(r"/dataset_description.json")

    def make(self, force=False):
        self._removeRedundant()
        
        exists, msg = checkPath(self.root)
        if not exists:
            raise FileExistsError(msg)
        
        for child in self.children:
            child.createBIDS()
        return
    
    def _removeRedundant(self):
        for child in self.children:
            if child:
                child._removeRedundant()
            else:
                child._deleteSelf()
                #consider using __del__ method in order to just call pop. Concerns around whether the garbage collection always occurs

                self.children.pop(child)

    def read(self, path:str = None):
        if path:
            self.root = path

        exists, msg = checkPath(self.root)
        if not exists():
            raise FileExistsError(msg)

        self.initialised = True
    
    def addSubject():
        pass

    """"
    reading files
        -tsv
        -json

    data specific       -sql queries
        -mne.io.raw
    """