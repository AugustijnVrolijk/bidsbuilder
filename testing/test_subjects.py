from bidsbuilder import *

def should_build():
    folderPath = r"C:\Users\augus\BCI_Stuff\Aspen\testing\test"
    subjects = ["mariana", "erdi"]
    session_name = "IEMU"

    myData = BidsDataset(folderPath)
    for sub in subjects:
        t1 = myData.add_subject(sub)
        ses1 = t1.add_session(session_name)

    myData.build(force=True)

def should_error():
    folderPath = r"C:\Users\augus\BCI_Stuff\Aspen\testing\test"
    subjects = ["mariana", "erdi","erdi"]
    session_name = "IEMU"

    myData = BidsDataset(folderPath)
    for sub in subjects:
        t1 = myData.add_subject(sub)
        ses1 = t1.add_session(session_name)

    myData.build(force=True)


if __name__ == "__main__":
    should_build()
