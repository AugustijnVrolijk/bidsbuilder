from functools import wraps
from pathlib import Path
from wrapBIDS.Modules.coreModule import DatasetCore
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


class coreFileWrapper(DatasetCore):
    
    @convertPath
    def __init__(self, level, stem = None, extensions = None):
        self.level = level
        self.stem = stem
        self.extensions = extensions

        if not stem:
            raise ValueError(f"stem {stem} must be defined as a string representing the path with no extensions")

        if self.extensions:
            self.isFile = True
        else:
            self.isFile = False

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

class coreJSON(coreFileWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass
    
class coreTSV(coreFileWrapper):
    def __init__(self, level, stem=None, extensions=None):
        super().__init__(level, stem, extensions)
        pass
    
class coreUnknown(coreFileWrapper):
    def __init__(self, level, stem=None, extensions=None):
        super().__init__(level, stem, extensions)
        pass

class coreFolder(coreFileWrapper):
    def __init__(self, level, stem=None, extensions=None):
        super().__init__(level, stem, extensions)
        pass


@convertPath
def resolveCoreClassType(*args, **kwargs) -> DatasetCore:
    """Resolve by looking at extensions"""
    extensions = kwargs.get("extensions", [])

    if ".json" in extensions and len(extensions) == 1:
        cls = coreJSON
    elif len(extensions) == 0:
        cls = coreFolder
    elif "json" in extensions and ".tsv" in extensions:
        cls = coreTSV
    else:
        cls = coreUnknown

    return cls(*args, **kwargs)

if __name__ == "__main__":
    test = coreJSON()