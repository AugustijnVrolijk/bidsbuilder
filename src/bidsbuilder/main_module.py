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
    initialised = False
    
    def __init__(self, root:str, minimal:bool=False):
        

        self.root = root
        self.schema:'Namespace' = parse_load_schema()
        self._tree_reference:Directory = Directory(_name=root, _file_link=self, _name_link=None, parent=None)
        from .modules import set_all_schema_
        set_all_schema_(self, self.schema)
        from .modules.file_bases.agnostic_files import _make_skeletonBIDS
        _make_skeletonBIDS(self.schema, self.tree, minimal)
        
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