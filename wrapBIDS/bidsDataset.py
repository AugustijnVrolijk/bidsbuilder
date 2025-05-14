from wrapBIDS.Modules import *
from wrapBIDS.util.util import checkPath
from wrapBIDS.Modules.commonFiles import resolveCoreClassType
import bidsschematools, bidsschematools.schema

class BidsDataset():
    initialised = False
    schema = bidsschematools.schema.load_schema()

    def __init__(self, root:str = None):
        self.children = {}
        self.root = root
        self.tree = {}
        DatasetCore.dataset = self
        self._make_skeletonBIDS()

    def _make_skeletonBIDS(self):

        exceptions = ["scans", "sessions", "phenotype"]
        for file in self.schema.rules.files.common.core.keys():
            self.children[file] = resolveCoreClassType(**self.schema.rules.files.common.core[file]._properties)
        
        for tabFile in self.schema.rules.files.common.tables.keys():
            if tabFile in exceptions:
                print(tabFile)
            else:
                self.children[file] = resolveCoreClassType(**self.schema.rules.files.common.core[file]._properties)

            """
            Exceptions for scans, sessions and phenotype
            """
            
        return

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