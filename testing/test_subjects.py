from bidsbuilder import *

def demo():
    folderPath = r"C:\Users\augus\BCI_Stuff\Aspen\testing\test"
    subjects = ["mariana", "erdi"]
    session_name = "IEMU"
    data = {"meta1": "value1", "meta2": 2}
    myData = BidsDataset(folderPath)
    for sub in subjects:
        t1 = myData.add_subject(sub)
        ses1 = t1.add_session(session_name)
        data1 = ses1.add_data
        for key, val in data.items():
            data1[key] = val

    myData.build(force=True)


if __name__ == "__main__":
    demo()
