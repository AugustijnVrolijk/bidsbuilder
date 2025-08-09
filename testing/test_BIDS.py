from bidsbuilder import *

def main():
    test1 = BidsDataset(root=r"C:\Users\augus\BCI_Stuff\Aspen\test")
    test1.dataset_description["Fundingasddas"] = "this is an example"
    hello = test1.addSubject("hello")
    hello.add_session("IEMU")
    tester2 = test1.addSubject("tester2")
    #ses_iemu = tester2.add_session("IEMU")
    #test1.addSubject("ASDASHDC138/(3)")
    #test1.addSubject("hello")
    test1.tree.fetch("genetic_info.json").exists = True
    test1.build(True)

def demo():
    folderPath = r"C:\Users\augus\BCI_Stuff\Aspen\demo2"
    myData = BidsDataset(folderPath, minimal=True)
    subjects = ["mariana", "erdi"]
    for sub in subjects:
        print(sub)
        t1 = myData.addSubject(sub)
        print(t1._tree_link.name)
        t1.add_session("IEMU")
    myData.build(force=True)

def myCode():
    dataset = BidsDataset()
    dataset.fetch("genetic_info.json").exists = False

    dataset.build()

"""
THERE IS A BUG AT THE MOMENT MAIN CREATES A dataset_description with a missing "required" field.
i.e. the hooks are not working since I updated them; need to look into it.



data = addData()

data.sidecar[]


"""

if __name__ == "__main__":
    main()



"""
- TABULAR FILES
- DIRECTORIES

- ASPEN
- LOGGING
"""