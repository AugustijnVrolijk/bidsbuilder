from pathlib import Path

from typing import TYPE_CHECKING, Generator, Any, Callable

from ..util.util import isDir
from .filenames import agnosticFilename
from .dataset_tree import Directory, FileCollection, FileEntry
from .json_files import agnostic_JSONfile
from .tabular_files import tabularJSONFile, tabularFile
from .dataset_core import DatasetCore

if TYPE_CHECKING:
    from bidsschematools.types import Namespace

def _make_skeletonBIDS(schema:'Namespace', tree:'Directory', minimal:bool=False):
    """agnostic files are found in rules.files.common:
    this is seperated in tabular files, and core
    
    I still need to process individual entries seperately in both of these as core has
    got .jsons, folders and other randoms once (.cff for citation, readme etc...)
    And tabular has some core tabular, and some "core" tabular which are actually present
    every time for subjects or sessions... (scans.tsv, sessions.tsv etc..)
    
    If needed in the future can make resolve_class_type more robust by returning a is_table
    from iter_agnostic_file if it is yielding from rules.files.common.table

    Between is_table and is_dir (rules.directories.raw) that would mean only jsons and other random
    files need to be resolved
    """
    
    for file_info, is_dir in _iter_agnostic_files(schema):
           
        c_f_info = _clean_file_info(file_info)
        class_builder = _resolve_class_type(c_f_info, is_dir)
        class_builder(c_f_info, tree, minimal)
        
    return

def _iter_agnostic_files(schema:'Namespace') -> Generator[tuple['Namespace', bool], None, None]:    
    exceptions = ["scans", "sessions", "phenotype"]

    def _iter_schema_file(to_iter:'Namespace'):

        for file in to_iter.keys():
            if file in exceptions:
                continue
            is_dir = isDir(schema.rules.directories.raw, file) #check if file is named in the directories schema
            
            yield (to_iter[file], is_dir)

    yield from _iter_schema_file(schema.rules.files.common.core)
    yield from _iter_schema_file(schema.rules.files.common.tables)

def _clean_file_info(file_info:'Namespace') -> dict:

    properties = file_info._properties

    extensions:list = properties.get("extensions", [])
    stem = properties.get("stem", None)    
    path = properties.pop("path", None)

    if path and stem:
        raise ValueError(f"path {path} and stem {stem} cannot both be defined")

    if path:
        tPath = Path(path)
        stem = tPath.stem
        pathExt = ''.join(tPath.suffixes) #merge for stuff like .tar.gz, instead of getting ['.tar', '.gz']
        if pathExt:
            extensions.append(pathExt)

    properties["extensions"] = extensions
    properties["stem"] = stem

    return properties

def _resolve_class_type(file_info:dict[str, Any], is_dir:bool=False) -> Callable[[dict, 'Directory'], None]:
    """

    """
    extensions = file_info["extensions"]
    #stem = file_info["stem"]

    if is_dir:
        return _process_folder
    elif ".json" in extensions and len(extensions) == 1:
        return _process_JSON
    #this seems to be enough logic at the moment, but could look at only considering if .tsv is present
    elif ".json" in extensions and ".tsv" in extensions:
        return _process_TSV
    else:
        return _process_UNKNOWN

def _process_folder(file_info:dict[str, Any], tree:'Directory', minimal:bool=False) -> Directory:
    assert file_info["extensions"] == []
    filename = agnosticFilename(file_info["stem"])
    file = DatasetCore(_level=file_info["level"])
    if minimal:
        file.exists = False
    tree.add_child(filename,file,type_flag="directory")
    return


def _process_JSON(file_info:dict[str, Any], tree:'Directory', minimal:bool=False) -> FileEntry:
    assert file_info["extensions"] == [".json"]
    filename = agnosticFilename(file_info["stem"], [".json"], ".json")
    file = agnostic_JSONfile(_level=file_info["level"])
    if minimal:
        file.exists = False
    tree.add_child(filename, file, "file")
    #no need to assign links, as creating a FileEntry does this
    return

def _process_TSV(file_info:dict[str, Any], tree:'Directory', minimal:bool=False) -> FileCollection:
    col_name = agnosticFilename(file_info["stem"])
    ret_obj = tree.add_child(col_name, None, 'collection')
    #tsv:
    filename = agnosticFilename('', [".tsv"], ".tsv")
    file = tabularFile(_level=file_info["level"])
    if minimal:
        file.exists = False
    ret_obj.add_child(filename, file)
    #json:
    filename = agnosticFilename('', [".json"], ".json")
    file = tabularJSONFile(_level=file_info["level"])
    if minimal:
        file.exists = False
    ret_obj.add_child(filename, file)
    return

def _process_UNKNOWN(file_info:dict[str, Any], tree:'Directory', minimal:bool=False) -> FileEntry:
    if len(file_info["extensions"]) == 0:
        cur_ext = ''
    else:
        cur_ext = file_info["extensions"][0]
    filename = agnosticFilename(file_info["stem"], file_info["extensions"], cur_ext)
    file = DatasetCore(_level=file_info["level"])
    tree.add_child(filename, file, "file")
    #no need to assign links, as creating a FileEntry does this
    if minimal:
        file.exists = False
    return