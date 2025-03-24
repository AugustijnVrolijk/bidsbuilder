import os
from util.queryASPEN import queryASPEN
from util.util import popDicts
from bids_dataset import DatasetModule
from typing import TYPE_CHECKING
 
if TYPE_CHECKING:
    from deps.bids_dataset import BidsDataset

class DatasetDescription(DatasetModule):
    def __init__(self, parent:"BidsDataset"):
        super().__init__(self, parent)

        self.JSONpath = os.path.join(self.parent.root, "dataset_description.json")
        
        #TO IMPLEMENT: KEY "DatasetLinks" IS REQUIRED IF URI's are used  
        self.recommended
        reqs = ["Name", "BIDSVersion"]

        #TO IMPLEMENT: KEY "Authors" is RECOMMENDED if Citation.cff is not present 
        #SEE NOTE BELOW for GeneratedBy   

        reco = ["HEDVersion", "DatasetType", "License", "GeneratedBy", "SourceDatasets"]

        opts = ["Acknowledgements", "HowToAcknowledge", "Funding", "EthicsApprovals", "ReferencesAndLinks", "DatasetDOI"] 

        popDicts((self.required, reqs),(self.recommended, reco),(self.optional, opts))

    def query(self):
        self.query = ""
        return self.query

    def setup(self):
        pass

    def createBIDS(self):

        for child in self.children:
            child.createBIDS()
        return


def getGeneratedBy():
    from checks.checks import checkValidURI

    container = {
       "Type":None,
       "Tag":None,
       "URI":None,
    } 
    checkValidURI(container["URI"])

    generatedByDict = {
       "Name":None,
       "Version":None,
       "Description":None,
       "CodeURL":None,
       "Container":container
    } 
    return generatedByDict

"""
    # Hardcoded metadata
    description_data = {
        "Name": "iEEG Dataset 24H for Graz",
        "BIDSVersion": "1.6.0",
        "Authors": ["Hugo Sturkenboom, etc."],

    }

    # If the file already exists, merge with existing content
    if description_file.exists():
        print(f"Updating existing dataset_description.json: {description_file}")
        with open(description_file, "r") as f:
            existing_data = json.load(f)
        description_data = {**existing_data, **description_data}  # Merge existing and new data

    # Write to the dataset_description.json file
    with open(description_file, "w") as f:
        json.dump(description_data, f, indent=4)

    print(f"Dataset description saved at {description_file}")

"""

def main():
    from bids_dataset import BidsDataset
    test1 = BidsDataset("C:/Home")
    test2 = DatasetDescription(test1)
    
    print("hi")
if __name__ == "__main__":
    main()