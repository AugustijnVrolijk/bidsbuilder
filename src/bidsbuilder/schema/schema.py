from functools import lru_cache
from bidsschematools.types import Namespace
from bidsschematools.schema import dereference, flatten_enums, _get_bids_version, _get_schema_version, _find
from bidsschematools.utils import get_bundled_schema_path

from .interpreter.selectors import selectorHook

def filter_schema(schema:Namespace):
    del schema["meta"]
    del schema.rules["checks"]
    del schema.rules.files["deriv"]
    del schema.rules.sidecars["derivatives"]
    del schema.rules.tabular_data["derivatives"]

def interpret_schema(schema:Namespace):
    
    #IMPORTANT, CAN ONLY SET BY DOING schema["KEY"] = , setting by doing schema.key = DOES NOT WORK

    for struct in _find(schema, lambda obj: ("selectors" in obj) or ("checks" in obj)):
    #for struct in _find(schema, lambda obj: "selectors" in obj):
        if "selectors" in struct:
            t_selector = selectorHook.from_raw(struct["selectors"])
            struct.update({"selectors": t_selector})

        if "checks" in struct:
            t_selector = selectorHook.from_raw(struct["checks"])
            struct.update({"checks": t_selector})
            
def recursive_interpret(rec_n, schema):
        #recurse into a file, i.e.
        #rec_n = 0 means we have a file, so then loops for each selector block, and then chooses selectors
        #rec_n = 1 means we have a folder of files,
        #rec_n = 2 means we have a folder of folders that need to be iterated all
    if rec_n >= 1:
        for key in schema.keys():
            schema[key] = recursive_interpret((rec_n-1), schema[key])

    else:
        for sel in schema.keys():
            t_selector = selectorHook.from_raw(schema[sel].selectors)
            #the raw schema is cached
            schema[sel]["selectors"] = t_selector

    return schema

@lru_cache
def parse_load_schema(schema_path=None, debug=False) -> Namespace:
    """Load and Parse the schema into a dictionary.

    This function allows the schema, like BIDS itself, to be specified in
    a hierarchy of directories and files.
    Filenames (minus extensions) and directory names become keys
    in the associative array (dict) of entries composed from content
    of files and entire directories.

    Parameters
    ----------
    schema_path : str, optional
        Directory containing yaml files or yaml file. If ``None``, use the
        default schema packaged with ``bidsschematools``.

    Returns
    -------
    dict
        Schema in dictionary form.

    Notes
    -----
        This function is cached, so it will only be called once per schema path.
    """
    if schema_path is None:
        schema_path = get_bundled_schema_path()
        #lgr.info("No schema path specified, defaulting to the bundled schema, `%s`.", schema_path)
    schema = Namespace.from_directory(schema_path)
    if not schema.objects:
        raise ValueError(f"objects subdirectory path not found in {schema_path}")
    if not schema.rules:
        raise ValueError(f"rules subdirectory path not found in {schema_path}")
    
    dereference(schema)
    flatten_enums(schema)
    
    schema["bids_version"] = _get_bids_version(schema_path)
    schema["schema_version"] = _get_schema_version(schema_path)

    if not debug:
        filter_schema(schema)
        interpret_schema(schema)
    return schema
