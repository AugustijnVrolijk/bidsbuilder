from ..modules.schema_objects import Metadata
from ..modules.core.dataset_core import DatasetCore

from typing import TYPE_CHECKING, Generator, Union

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace
    from .interpreter.selectors import selectorHook

def _process_fields_add(fields:'Namespace') -> dict:
    """convert the fields namespace into a metadata dict"""
    processed = {}
    for key in fields.keys():
        if isinstance(fields[key], str): #the value is a requirement
            processed[key] = (fields[key], Metadata(key, None))
        else:
            level = fields[key].pop("level")
            met_instance = Metadata(key, None)
            Metadata._override[met_instance] = fields[key]
            processed[key] = (level, met_instance)
    return processed

def _process_fields_del(fields:'Namespace') -> dict:
    """convert the fields namespace into a list of keys to delete"""
    processed = fields.keys()
    return processed

def JSON_check_schema(reference:'DatasetCore',
                       schema:'Namespace', 
                       cur_labels:set=set(), 
                       add_callbacks:bool=False, 
                       tags:Union[str, list] = []) -> Generator[tuple, None, None]:
    """
    generator, which when given: a JSON object to check,
                                a schema,
                                Optionally: a list of current labels
                                            a bool to add callbacks,
                                            a list of tags to check
                                            
    yields tuples of the format: 
    ("add"/"del", label, fields)
    the first variable tells whether to add or remove the given fields
    """
    for label, _sub_schema in _recurse_schema_explore(schema):
        cur_selector:'selectorHook' = _sub_schema["selectors"]
        if not check_tags(cur_selector, tags):
            continue

        is_true = cur_selector(reference, add_callbacks=add_callbacks)
        if is_true and (label not in cur_labels):
            metadata_dict = _process_fields_add(_sub_schema["fields"])
            yield ("add", label, metadata_dict)
        elif (not is_true) and (label in cur_labels):
            labels_list = _process_fields_del(_sub_schema["fields"])
            yield ("del", label, labels_list)
    return

def check_tags(selHook:'selectorHook', tags:Union[str, list]=None) -> bool:
    if isinstance(tags, str):
        tags:list = [tags]

    if not tags:  # no tags defined, check all
        return True

    for tag in tags:
        if tag in selHook.tags:
            return True        
    return False

def _recurse_schema_explore(schema:'Namespace') -> Generator:
    """
    Recursively yield schema keys up to cls._recurse_depth levels.
    """

    for key, value in schema.items():
        if "selectors" in value.keys():
            yield key, value
        else:
            yield from _recurse_schema_explore(value)
