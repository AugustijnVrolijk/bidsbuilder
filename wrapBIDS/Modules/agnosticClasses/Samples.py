import os
from typing import TYPE_CHECKING
from wrapBIDS.Modules.datasetModule import DatasetCore

if TYPE_CHECKING:
    from wrapBIDS.bidsDataset import BidsDataset

class Samples(DatasetCore):
    def __init__(self, parent:"BidsDataset"):
        self.path = os.path.join(parent.root, "samples")
        self.extensions = [".tsv", ".json"]
        pass