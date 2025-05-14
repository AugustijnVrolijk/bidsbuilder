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

