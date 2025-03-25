from wrapBIDS.Classes.agnosticClasses import *

class BidsDataset():
    def __init__(self, root):
        self.children = {} 
        self.root = root 
        
        self._createAgnosticFiles()


    def _createAgnosticFiles(self):
        self.description = Description(self)
        self.readme = Readme(self)
        self.participants = Participants(self)
        self.citation = Citation(self)
        self.changes = Changes(self)
        self.license = License(self)
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

    def updateDescription(self, **kwargs):
        self.description.update(kwargs)
        return
    


    """"
    reading files
        -tsv
        -json

    data specific       -sql queries
        -mne.io.raw

           
    
    
    """