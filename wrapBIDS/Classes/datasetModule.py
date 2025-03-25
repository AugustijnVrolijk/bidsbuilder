from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wrapBIDS.Classes.bidsDataset import BidsDataset


class DatasetCore():
    def __init__(self, parent):
        self.parent = parent
        pass

    def _write_BIDS(self):
        pass

    def _read_BIDS(self):
        pass

class DatasetModule(DatasetCore):
    def __init__(self, parent:"BidsDataset"):
        super().__init__(parent)
        self.required = {}
        self.recommended = {} 
        self.optional = {}

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

    
