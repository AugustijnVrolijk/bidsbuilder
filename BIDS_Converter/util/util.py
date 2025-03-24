from typing import Any

def popDicts(*args, val:Any = None):
    dicts = [] 
    for pair in args:
        dictToPop = pair[0]
        labelList = pair[1]
        assert isinstance(dictToPop, dict) and isinstance(labelList, list)
        dicts.append(popDict(dictToPop, labelList, val))
    return dicts

def popDict(toPop:dict, Labels:list, val:Any = None):
    for label in Labels:
        toPop[str(label)] = val 
    return toPop


def testPopDicts():
    test1 = {} 
    label1 = ["test1_1", "test1_2", "test1_3"] 
    test2 = {} 
    label2 = ["test2_1", "test2_2", "test2_3"]

    test3 = popDict(test1, label1, 10)
    verify3 = {"test1_1":10, "test1_2":10, "test1_3":10}

    assert test3 == verify3 and test1 == verify3
  
    test4 = popDicts((test1, label1), (test2, label2))
    verify4_1 = {"test1_1":None, "test1_2":None, "test1_3":None}
    verify4_2 = {"test2_1":None, "test2_2":None, "test2_3":None}
    assert test1 == verify4_1 and test2 == verify4_2
    verify4 = [verify4_1, verify4_2] 
    assert test4 == verify4

    test5 = popDicts((test1, label1), (test2, label2), val="val1")
    verify5_1 = {"test1_1":"val1", "test1_2":"val1", "test1_3":"val1"}
    verify5_2 = {"test2_1":"val1", "test2_2":"val1", "test2_3":"val1"}
    assert test1 == verify5_1 and test2 == verify5_2
    verify5 = [verify5_1, verify5_2] 
    assert test5 == verify5

    return


if __name__ == "__main__":
    testPopDicts()