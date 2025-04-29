from wrapBIDS.Modules.agnosticClasses import *
from wrapBIDS.util.util import checkPath
import bidsschematools, bidsschematools.schema

class BidsDataset():
    initialised = False
    schema = bidsschematools.schema.load_schema()

    def __init__(self, root:str = None):
        self.children = {}
        self.root = root
        self._make_skeletonBIDS()

    """
    def _createCommon(self):
        self.description = Description(self)
        self.readme = Readme(self)
        self.participants = Participants(self)
        self.citation = Citation(self)
        self.changes = Changes(self)
        self.license = License(self)
        self.children["description"] = self.description
        self.children["readme"] = self.readme
        self.children["participants"] = self.participants
    """

    def _make_skeletonBIDS(self):
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