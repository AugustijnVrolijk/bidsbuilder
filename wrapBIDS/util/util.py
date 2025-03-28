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

if __name__ == "__main__":
    pass