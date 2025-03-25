from wrapBIDS.Classes.agnosticClasses import *

class BidsDataset():
    def __init__(self, root):
        self.children = {} 
        self.root = root 
        
        self._createAgnosticFiles()


    def _createAgnosticFiles(self):
        self.description = DatasetDescription(self)
        self.readme = DatasetReadme(self)
        self.participants = DatasetParticipants(self)
        self.citation = ""
        self.changes = ""
        self.license = ""
        self.children["description"] = self.description
        self.children["readme"] = self.readme
        self.children["participants"] = self.participants
        

    def createBIDS(self):

        for child in self.children:
            child.createBIDS()
        return
    
    def readBIDS(self):
        for child in self.children:
            child.readBIDS()