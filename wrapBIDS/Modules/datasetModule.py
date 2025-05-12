from typing import TYPE_CHECKING
from wrapBIDS.util.categoryDict import catDict

if TYPE_CHECKING:
    from wrapBIDS.bidsDataset import BidsDataset


class DatasetCore():
    dataset:"BidsDataset" = None
    def __init__(self):
        pass

    def _write_BIDS(self):
        pass

    def _read_BIDS(self):
        pass

    def deleteSelf(self):
        return
    
    def __contains__(self, key): #used for selector parsing "in", need it to point it to whatever is needed
        return

class JSONFile(DatasetCore):
    pass

class TSVFile(DatasetCore):
    pass

class coreFileWrapper(DatasetCore):
    def __init__(self, level, path = None, stem = None, entities = None, extensions = None):
        self.level = level
        self.path = path
        self.stem = stem
        self.entities = entities
        self.extensions = extensions
        print(level)
        print(path)
        print(stem)
        print(entities)
        print(extensions)
        exit()
        self.params = catDict()
        pass

    def populateVals(self):
        pass

    def checkVals(self):
        for key, val in self.required:
            if isinstance(val, None):
                KeyError(f"no value for required field:{key}")

        for key, val in self.recommended:
            if isinstance(val, None):
                Warning(f"no value for recommended field:{key}")
        pass

    
