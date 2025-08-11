from bidsbuilder import *

def main():
    test1 = BidsDataset(root=r"C:\Users\augus\BCI_Stuff\Aspen\test")
    test1.dataset_description["Authors"] = "Augustijn Vrolijk"
    hello = test1.addSubject("hello")
    hello.add_session("IEMU")
    tester2 = test1.addSubject("tester2")
    #ses_iemu = tester2.add_session("IEMU")
    #test1.addSubject("ASDASHDC138/(3)")
    #test1.addSubject("hello")
    test1.tree.fetch("genetic_info.json").exists = True
    test1.tree.fetch("CITATION.cff").exists = False
    test1.build(True)


def test_system_tests_basic():
    test1 = BidsDataset(root=r"C:\Users\augus\BCI_Stuff\Aspen\test")

    assert test1.dataset_description.metadata["Genetics"].level == "required"
    test1.tree.fetch("genetic_info.json").exists = False
    assert "Genetics" not in test1.dataset_description.metadata

    test1.dataset_description["Authors"] = "Augustijn Vrolijk"
    assert test1.dataset_description.metadata["Authors"].level == "optional"
    test1.tree.fetch("CITATION.cff").exists = False
    assert test1.dataset_description.metadata["Authors"].level == "recommended"

def demo():
    folderPath = r"C:\Users\augus\BCI_Stuff\Aspen\demo2"
    myData = BidsDataset(folderPath)
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

if __name__ == "__main__":
    demo()



"""
- TABULAR FILES
- DIRECTORIES

- ASPEN
- LOGGING
"""