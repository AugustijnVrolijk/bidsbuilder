from functools import wraps
from pathlib import Path
from bidsbuilder.modules.coreModule import DatasetCore

from typing import TYPE_CHECKING


def convertPath(cls):
    """
    ensures no clashes between path stem and entities, also converts path into stem and entities for easier downstream parsing
    """
    @wraps(cls)
    def wrapper(*args, **kwargs):
        path = kwargs.pop("path", None)
        stem = kwargs.get("stem", None)
        extensions = kwargs.get("extensions", [])
        
        if path and stem:
            raise ValueError(f"path {path} and stem {stem} cannot both be defined")

        if path:
            tPath = Path(path)
            pathExt = ''.join(tPath.suffixes)
            if pathExt:
                extensions.append(pathExt)
                kwargs["extensions"] = extensions
            kwargs["stem"] = tPath.stem

        return cls(*args, **kwargs)
    return wrapper

class corePath(DatasetCore):
    @convertPath
    def __init__(self, level, name = None):
        super().__init__(name, level=level)
        self.level = level
        self.name = name

        if not name:
            raise ValueError(f"stem {name} must be defined as a string representing the path with no extensions")

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, _:str):
        #can't change names for core files
        return 

    def _getPaths(self):
        paths = []
        if self.extensions:
            for ext in self.extensions:
                paths.append(self.stem + ext)
        else:
            paths.append(self.stem)
        return paths

    def populateVals(self):
        pass

    def checkVals(self):
        for key, val in self.required:
            if isinstance(val, None):
                KeyError(f"no value for required field:{key}")

        for key, val in self.recommended:
            if isinstance(val, None):
                Warning(f"no value for recommended field:{key}")
        pass

class coreJSON(corePath):
    def __init__(self, level:str, stem:str, extensions:list):
        #extensions is a list
        self.extension = extensions[0]
        assert self.extension == ".json"
        name = stem + self.extension
        super().__init__(level=level, name=name)
    
class coreTSV(corePath):
    def __init__(self, level:str, stem:str, extensions:list):
        self.extensions = extensions
        self.stem = stem
        assert ".tsv" in self.extensions
        name = stem + ".tsv"
        super().__init__(level=level, name=name)

class coreUnknown(corePath):
    def __init__(self, level:str, stem:str, extensions:list=[]):
        self.extensions = extensions
        self.stem = stem
        if self.extensions:
            name = stem + self.extensions[0]
        else:
            name = stem
        super().__init__(level=level, name=name)

class coreFolder(corePath):
    def __init__(self, level:str, stem:str):
        super().__init__(level=level, name=stem)


@convertPath
def resolveCoreClassType(*args, is_dir:bool=False,**kwargs) -> corePath:
    """Resolve by looking at extensions
    
    Should look into something more robust
    """


    extensions = kwargs.get("extensions", [])
    if is_dir:
        cls = coreFolder
    elif ".json" in extensions and len(extensions) == 1:
        cls = coreJSON
    #this seems to be enough logic at the moment, but could look at only considering if .tsv is present
    elif ".json" in extensions and ".tsv" in extensions:
        cls = coreTSV
    else:
        cls = coreUnknown

    return cls(*args, **kwargs)

if __name__ == "__main__":
    test = coreJSON()