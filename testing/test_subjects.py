from bidsbuilder import *

def demo():
    folderPath = r"C:\Users\augus\BCI_Stuff\Aspen\testing\test"
    myData = BidsDataset(folderPath)
    subjects = ["mariana", "erdi"]
    for sub in subjects:
        t1 = myData.add_subject(sub)
        t1.add_session("IEMU")
    myData.build(force=True)



if __name__ == "__main__":
    demo()
