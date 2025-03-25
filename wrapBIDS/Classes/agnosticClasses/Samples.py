import os
from typing import TYPE_CHECKING
from wrapBIDS.Classes.datasetModule import DatasetCore

if TYPE_CHECKING:
    from wrapBIDS.Classes.bidsDataset import BidsDataset

class Samples(DatasetCore):
    def __init__(self, parent:"BidsDataset"):
        self.path = os.path.join(parent.root, "samples")
        self.extensions = [".tsv", ".json"]
        pass