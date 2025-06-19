from pathlib import Path

from .modules import *
from .util.util import checkPath, isDir, clearSchema
from .util.datasetTree import FileTree
from .util.schema import parse_load_schema
from .modules.commonFiles import resolveCoreClassType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import MutableMapping 

class BidsDataset():
    initialised = False

    schema = parse_load_schema()

    def __init__(self, root:str = Path.cwd()):
        self.root = root
        self._tree_reference = FileTree(_name=root, link=self, parent=None)
        DatasetCore.dataset = self
        DatasetSubject.dataset = self

        self._make_skeletonBIDS()
        self._interpret_skeletonBIDS()

    def _make_skeletonBIDS(self):

        #Exceptions for scans, sessions and phenotype
        exceptions = ["scans", "sessions", "phenotype"]

        def _pop_from_schema(schema:'MutableMapping'):
            toPop = []
            for file in schema.keys():
                if file in exceptions:
                    continue
                is_dir = isDir(self.schema.rules.directories.raw, file)
                tObj = resolveCoreClassType(**schema[file]._properties, is_dir=is_dir)
                #NEED TO UPDATE IT TO GIVE THE NAME RATHER THAN THE STEM
                self._tree_reference.addPath(tObj.name, tObj, is_dir)
                toPop.append(file)

            for key in toPop:
                schema.pop(key)
                
        _pop_from_schema(self.schema.rules.files.common.core)
        clearSchema(self.schema.rules.files.common, "core")

        _pop_from_schema(self.schema.rules.files.common.tables)
        clearSchema(self.schema.rules.files.common, "tables")
        return

    def _interpret_skeletonBIDS(self):
        f1 = self.tree.fetch("README")
        f2 = self.tree.fetch("dataset_description.json")
        #recursive_interpret(1, self.schema.rules.files.common)
        print(f1._tree_reference)
        print(f2._tree_reference)
        print(self.schema.rules.dataset_metadata.dataset_description.selectors.funcs[0])
        print(self.schema.rules.dataset_metadata.dataset_authors.selectors.funcs[0])
        print(self.schema.rules.dataset_metadata.dataset_authors.selectors.funcs[1])

        print(self.schema.rules.dataset_metadata.dataset_description.selectors(f1))
        print(self.schema.rules.dataset_metadata.dataset_description.selectors(f2))
        print(self.schema.rules.files.raw.motion)
        print("hello")
        return

    @property
    def tree(self):
        return self._tree_reference

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
        

        """
        do some stuff
        """

        self.initialised = True
        
    """"
    reading files
        -tsv
        -json

    data specific       -sql queries
        -mne.io.raw
    """

if __name__ == "__main__":
    test = BidsDataset()
    test.tree.fetch("/stimuli")
    print("hello")