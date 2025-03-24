from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from BIDS_Converter.Classes.bidsDataset import BidsDataset


class DatasetModule():
    def __init__(self, parent:"BidsDataset"):
        self.parent = parent
        self.required = {}
        self.recommended = {} 
        self.optional = {}
        

        self.setup()
        pass

    def setup(self):
        result = self.fetchQuery()
        self.populateVals(result)

    def fetchQuery(self):
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

    def createBIDS(self):
        pass