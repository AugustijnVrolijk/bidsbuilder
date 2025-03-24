from BIDS_Converter.Classes.bidsDataset import BidsDataset
"""
21/03/2025 Augustijn Vrolijk

pipeline -> ASPEN request: 
                    -inputs:
                        -needed info to begin:
                            -root path
                            -subjects, tasks etc...
                            -experiments etc..

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


"""



def main():
      
    
    bids = BidsDataset()


if __name__ == "__main__":
    main()