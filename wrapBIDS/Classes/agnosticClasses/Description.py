import os
from wrapBIDS.util.io import _read_JSON
from wrapBIDS.Classes.datasetModule import DatasetModule
from mne.utils import logger
from typing import TYPE_CHECKING
 
if TYPE_CHECKING:
    from wrapBIDS.Classes.bidsDataset import BidsDataset

class Description(DatasetModule):
    def __init__(self, parent:"BidsDataset"):
        super().__init__(parent)
        self.path = os.path.join(parent.root, "dataset_description.json")
        
        #TO IMPLEMENT: KEY "DatasetLinks" IS REQUIRED IF URI's are used  
        self.required = ["Name", "BIDSVersion"]
        #TO IMPLEMENT: KEY "Authors" is RECOMMENDED if Citation.cff is not present 
        #SEE NOTE BELOW for GeneratedBy   
        self.recommended = ["HEDVersion", "DatasetType", "License", "GeneratedBy", "SourceDatasets", "Authors", "DatasetLinks"]
        self.optional = ["Acknowledgements", "HowToAcknowledge", "Funding", "EthicsApprovals", "ReferencesAndLinks", "DatasetDOI"] 


    def readCurrent(self):
        curData = _read_JSON(self.path)
        self.params.populateSelf(rawDict=curData, required=self.required, recommended=self.recommended, optional=self.optional)
        logger.info(f"successfully populated {self} from {self.path}")

    def createBIDS(self):

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

"""

