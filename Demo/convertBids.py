from wrapBIDS.Classes import *
from wrapBIDS.Classes.agnosticClasses import *
"""
21/03/2025 Augustijn Vrolijk

pipeline -> ASPEN request: 
                    -inputs:
                        -needed info to begin:
                            -root path
                            -subjects, tasks etc...
                            -experiments etc..
                    
                    -need to make sure I have a good input, i.e

                    -create BidsDataset object
                        -which creates sub objects depending on the input info
                        -each sub object queries database for needed info based on inputs
                        (high level stuff is asked i.e. participants, paths to the data etc.., shouldnt be much memory space)
                        
                    -check if enough info is here
                        -either then continue or pause to ask for more info (lacking in database etc..)

                    create bids folder
                        -now create the objects from the metadata as well as fetching and if needed converting the raw data
                        can parallise this, i.e. create a pool of threads each doing the creating for a subject folder etc..

                    return exit status


BIDS take as input pandas dataframes. So that whole bit is fully able to be public, 
then on this end we have to create a couple scripts to populate pandas dataframes from the sql database
i.e. a couple queries that are used.
"""

"""
skeleton class, defining whether to add stuff like license.cff and other stuff

generate bids_dataset
populate it:

main():
    bids = bids_dataset()
    bids.addDescription(info needed)
    bids.addParticipants(stuff)

or

main():
    bids = bids_dataset(path)
    bids.readBids()
    bids.addSubject(subject name)

    (read the bids structure and populate objects from what is already there)

"""



def main():
    rootStr = "C:/Home"
    test1 = BidsDataset(root=rootStr)
    test2 = Description(test1)
    print("hi")

if __name__ == "__main__":
    main()
