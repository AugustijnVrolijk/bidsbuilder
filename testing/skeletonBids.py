

class skeletonBidsDataset():
    def __init__(self, root):
        self.children = {} 
        self.root = root 
        
        self._createAgnosticFiles()


    def _createAgnosticFiles(self):
        description = "DatasetDescription(self)"
        readme = "DatasetReadme(self)"
        participants = "DatasetParticipants(self)"
        
        self.children["description"] = description
        self.children["readme"] = readme
        self.children["participants"] = participants
        

    def createBIDS(self):

        for child in self.children:
            child.createBIDS()
        return
    