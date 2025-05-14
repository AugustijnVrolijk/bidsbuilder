import os
from wrapBIDS.Modules.coreModule import DatasetModule

from typing import TYPE_CHECKING
 
if TYPE_CHECKING:
    from wrapBIDS.bidsDataset import BidsDataset


class Participants(DatasetModule):
    def __init__(self, parent:"BidsDataset"):
        super().__init__(parent)
        self.path = os.path.join(parent.root, "dataset_description.json")

    def updateVals(self):
        pass


def main():
    pass

if __name__ == "__main__":
    main()