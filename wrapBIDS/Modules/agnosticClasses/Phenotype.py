import os
from typing import TYPE_CHECKING
 
if TYPE_CHECKING:
    from wrapBIDS.bidsDataset import BidsDataset

class Phenotype():
    def __init__(self, parent:"BidsDataset"):
        self.path = os.path.join(parent.root, "dataset_description.json")
