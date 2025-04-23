import os
from typing import Any, Tuple
from pathlib import Path

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

def _getPathStatus(path:str) -> Tuple[int, int, str, str]:
    """
    check if a given directory path is valid

    input: path
    returns two integer flags and two string messages
        path status: whether the path is a valid, directory, exists or not, and if it is imaginary whether it would be a valid dir
            level:
                -1: invalid path
                0: valid path but doesn't exist yet
                1: valid path and already populated
                2: valid path and unpopulated

        permissions: whether the user has read/write access to the target directory
            level:
                -1: no access
                0:  read only
                1:  write only
                2:  both
        status msg: message describing the int1 flag value
        permission msg: message describing the int2 flag value
    """
    path = Path(path)
    checkVal = False

    if path.is_dir():
        checkVal = True
        exs_val = -1
        exs_msg = "target path is a directory but cannot be accessed"
    elif not path.exists() and not path.suffix:
        cur = path
        while True:
            path = path.parent
            if path == cur:
                exs_val = -1
                exs_msg = "target path does not contain an existing root"
                break

            if path.is_dir():
                exs_val = 0
                exs_msg = "target path does not exist yet but has a valid root"
                break
            cur = path
    else:
        exs_val = -1
        exs_msg = "target path is not a directory"

    if os.access(path, os.R_OK and os.W_OK):
        perms_val = 2
        perms_msg = "target dir has read and write access"
    elif os.access(path, os.W_OK):
        checkVal = False
        perms_val = 1
        perms_msg = "target directory has write access"
    elif os.access(path, os.R_OK):
        perms_val = 0
        perms_msg = "target directory has read access"
    else:
        checkVal = False
        perms_val = -1
        perms_msg = "target directory cannot be accessed"

    if checkVal:
        try:
            if any(path.iterdir()):
                exs_val = 1
                exs_msg = "target path is already populated"
            else:
                exs_val = 2
                exs_msg = "target path is not populated"
        except (PermissionError):
            exs_val = -1
            exs_msg = "target path is a directory but cannot be accessed"

    return exs_val, perms_val, exs_msg, perms_msg 

def checkPath(path:str, force:bool = False, flag:str=None) -> bool:
    """
    check path and create folder struct if necessary
    
    inputs: 
        - path: path to check
        - force: whether to ask the user about potential conflict or force path creation
        - flag: additional flags for different behaviour
            levels:
                -"read" doesn't matter if the folder doesn't have write permissions,
                can still read from the folder

    returns:
        - success: whether the path was successfully created/found depending on the flag
    
    """
    readOnly = False
    flag = flag.strip().lower()
    if flag == None:
        pass
    elif flag == "read":
        readOnly = True
    else:
        raise SyntaxError("unknown flag given to checkPath")
    
    exists, perm, exists_msg, perm_msg = _getPathStatus(path)

    if exists == -1: #folder is invald
        return False, exists_msg
    elif perm == -1 and exists != 0: #folder exists and has no permissions
        return False, perm_msg



    elif exists == 2:
        if getInput():
            return



        def getInput(msg:str, force:bool = False):
            if force:
                return True
            
            print(f"{msg}\nWould you like to continue anyway?\n(y\\n)")
            retval = False
            while True:
                val = input().strip().lower()
                yes = ("y", "yes", "ye")
                no = ("n", "no")
                if val in yes:
                    retval = True
                    break
                elif val in no:
                    retval = False
                    break
                print("Input not recognised, please input 'yes'/'y' or 'no'/'n' ")
            return retval
    return

def makeFolder(path:str):
    return

if __name__ == "__main__":
    paths = [r"C:\Users\augus\BCI_Stuff\Aspen\bids_conversion", 
             r"C:/Users/augus/BCI_Stuff/Aspen/bids_conversion/wrapBIDS/ut/il/tester/1/", 
             r"E:/Users",
             r"C:/",
             r"C:\Windows\System32\config",
             r"C:\\System Volume Information",
             r"C:\\$Recycle.Bin"]
    for path in paths:
        val1, val2, str1, str2 = _getPathStatus(path)
        print(f"{path}\n{val1}\n{str1}\n{val2}\n{str2}\n")