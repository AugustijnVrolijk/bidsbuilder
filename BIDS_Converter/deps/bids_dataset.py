import agnosticClasses as ac
import BIDS_Converter

class BidsDataset():
    def __init__(self, root):
        self.children = {} 
        self.root = root 
        
        self._createAgnosticFiles()
        pass


    def _createAgnosticFiles(self):
        description = ac.DatasetDescription()
        readme = ac.DatasetReadme()
        participants = ac.DatasetParticipants()
        self.children["description"] = description
        self.children["readme"] = readme
        self.children["participants"] = participants
        pass

    def createBIDS(self):

        for child in self.children:
            child.createBIDS()
        return
    