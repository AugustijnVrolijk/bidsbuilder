from functools import wraps
from pathlib import Path

from attrs import define, field
from typing import TYPE_CHECKING

from ..util.util import isDir, clearSchema
from .filenames import agnosticFilename

if TYPE_CHECKING:
    from .dataset_tree import Directory
    from bidsschematools.types import Namespace

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

@define(slots=True)
class corePath():

    level:str = field(repr=True)
    _name:str = field(repr=True, alias="_name")

    @property   #no setter, name can't be changed
    def name(self):
        return self._name
    """
    @DatasetCore.exists.setter
    def exists(self, value):
        if not isinstance(value, bool):
            raise TypeError(f"exists must be of type boolean not {type(value)} for {value}") 

        if self.level != "required":
            self._exists = value
    """
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

"""
@DatasetCore.exists.setter
    def exists(self, value):
        if not isinstance(value, bool):
            raise TypeError(f"exists must be of type boolean not {type(value)} for {value}") 

        if self.level != "required":
            self._exists = value
"""

@define(slots=True)
class coreJSON(corePath):
    def __init__(self, level:str, stem:str, extensions:list):
        #extensions is a list
        self.extension = extensions[0]
        assert self.extension == ".json"
        name = stem + self.extension
        super().__init__(level=level, name=name)
    
@define(slots=True)
class coreTSV(corePath):
    def __init__(self, level:str, stem:str, extensions:list):
        self.extensions = extensions
        self.stem = stem
        assert ".tsv" in self.extensions
        name = stem + ".tsv"
        super().__init__(level=level, name=name)

@define(slots=True)
class coreUnknown(corePath):
    def __init__(self, level:str, stem:str, extensions:list=[]):
        self.extensions = extensions
        self.stem = stem
        if self.extensions:
            name = stem + self.extensions[0]
        else:
            name = stem
        super().__init__(level=level, name=name)

@define(slots=True)
class coreFolder(corePath):
    
    def __init__(self, level:str, stem:str):
        super().__init__(level=level, name=stem)

def _make_skeletonBIDS(schema:'Namespace', tree:'Directory'):
    #Exceptions for scans, sessions and phenotype
    exceptions = ["scans", "sessions", "phenotype"]

    def _pop_from_schema(schema:'Namespace'):

        for file in schema.keys():
            if file in exceptions:
                continue
            is_dir = isDir(schema.rules.directories.raw, file) #check if file is named in the directories schema
            tObj = resolveCoreClassType(**schema[file]._properties, is_dir=is_dir)

            tree.addPath(tObj.name, tObj, is_dir)
            
    _pop_from_schema(schema.rules.files.common.core)
    _pop_from_schema(schema.rules.files.common.tables)
    return

def _interpret_skeletonBIDS(self):
    f1 = self.tree.fetch("README")
    f2 = self.tree.fetch("dataset_description.json")
    #recursive_interpret(1, self.schema.rules.files.common)
    print(f1._tree_reference)
    print(f2._tree_reference)
    print(self.schema.rules.dataset_metadata.dataset_description.selectors.funcs[0])
    print(self.schema.rules.dataset_metadata.dataset_authors.selectors.funcs[0])
    print(self.schema.rules.dataset_metadata.dataset_authors.selectors.funcs[1])

    print(self.schema.rules.dataset_metadata.dataset_description.selectors(f1))
    print(self.schema.rules.dataset_metadata.dataset_description.selectors(f2))
    print(self.schema.rules.files.raw.motion)
    print("hello")
    return

@convertPath
def resolveCoreClassType(*args, is_dir:bool=False,**kwargs) -> agnosticFilename:
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

    path = kwargs.pop("path", None)
    stem = kwargs.get("stem", None)
    
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

""" OLD VERSION:

def _make_skeletonBIDS(schema:'Namespace', tree:'Directory'):
    #Exceptions for scans, sessions and phenotype
    exceptions = ["scans", "sessions", "phenotype"]

    def _pop_from_schema(schema:'Namespace'):
        toPop = []
        for file in schema.keys():
            if file in exceptions:
                continue
            is_dir = isDir(schema.rules.directories.raw, file)
            tObj = resolveCoreClassType(**schema[file]._properties, is_dir=is_dir)

            tree.addPath(tObj.name, tObj, is_dir)
            toPop.append(file)
            
        for key in toPop:
            schema.pop(key)
            
    _pop_from_schema(schema.rules.files.common.core)
    clearSchema(schema.rules.files.common, "core")

    _pop_from_schema(schema.rules.files.common.tables)
    clearSchema(schema.rules.files.common, "tables")
    return
"""