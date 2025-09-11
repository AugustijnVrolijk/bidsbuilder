from ..modules.schema_objects import Metadata
from ..modules.core.dataset_core import DatasetCore

from typing import TYPE_CHECKING, Generator, Union, Any

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace
    from .interpreter.selectors import selectorHook

from abc import ABC, abstractmethod

class schema_checker_OLD(ABC):

    @abstractmethod
    def _process_add(cls, fields:'Namespace') -> Any:...

    @abstractmethod
    def _process_del(cls, fields:'Namespace') -> Any:...

    @classmethod
    def check_schema(cls, reference:'DatasetCore',
                        schema:'Namespace', 
                        cur_labels:set=None, 
                        add_callbacks:bool=False, 
                        tags:Union[str, list] = None) -> Generator[tuple[str, str, Any], None, None]:
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
        if cur_labels is None:
            cur_labels = set()
        if tags is None:
            tags = []

        for label, _sub_schema in cls._recurse_schema_explore(schema):
            cur_selector:'selectorHook' = _sub_schema["selectors"]
            if not cls.check_tags(cur_selector, tags):
                continue

            is_true = cur_selector(reference, add_callbacks=add_callbacks)
            if is_true and (label not in cur_labels):
                add_info = cls._process_add(_sub_schema)
                yield ("add", label, add_info)
            elif (not is_true) and (label in cur_labels):
                del_info = cls._process_del(_sub_schema)
                yield ("del", label, del_info)

    @staticmethod
    def check_tags(selHook:'selectorHook', tags:Union[str, list]=None) -> bool:
        if isinstance(tags, str):
            tags:list = [tags]

        if not tags:  # no tags defined, check all
            return True

        for tag in tags:
            if tag in selHook.tags:
                return True        
        return False

    @classmethod
    def _recurse_schema_explore(cls, schema:'Namespace') -> Generator:
        """
        Recursively yield schema keys up to cls._recurse_depth levels.
        """

        for key, value in schema.items():
            if "selectors" in value.keys():
                yield key, value
            else:
                yield from cls._recurse_schema_explore(value)


class schema_checker():

    @classmethod
    def check_schema(cls, reference:'DatasetCore',
                        schema:'Namespace', 
                        cur_labels:set=None, 
                        add_callbacks:bool=False, 
                        tags:Union[str, list] = None) -> Generator[tuple[str, str, Any], None, None]:
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
        if cur_labels is None:
            cur_labels = set()
        if tags is None:
            tags = []

        for label, _sub_schema in cls._recurse_schema_explore(schema):
            cur_selector:'selectorHook' = _sub_schema["selectors"]
            if not cls.check_tags(cur_selector, tags):
                continue

            is_true = cur_selector(reference, add_callbacks=add_callbacks)
            if is_true and (label not in cur_labels):
                yield ("add", label, _sub_schema)
            elif (not is_true) and (label in cur_labels):
                yield ("del", label, _sub_schema)

    @staticmethod
    def check_tags(selHook:'selectorHook', tags:Union[str, list]=None) -> bool:
        if isinstance(tags, str):
            tags:list = [tags]

        if not tags:  # no tags defined, check all
            return True

        for tag in tags:
            if tag in selHook.tags:
                return True        
        return False

    @classmethod
    def _recurse_schema_explore(cls, schema:'Namespace') -> Generator:
        """
        Recursively yield schema keys up to cls._recurse_depth levels.
        """

        for key, value in schema.items():
            if "selectors" in value.keys():
                yield key, value
            else:
                yield from cls._recurse_schema_explore(value)

check_schema = schema_checker.check_schema

__all__ = ["check_schema"]