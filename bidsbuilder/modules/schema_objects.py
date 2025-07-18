import re

from attrs import define, field
from typing import Union, ClassVar, TYPE_CHECKING
from functools import lru_cache

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace


"""
need to be able to overwrite certain values, like the format, enum etc... 
i.e. in meg.yaml, the acq entity can only be "crosstalk"

can either add an override dictionary to valueBase, nameValueBase etc... where when fetching schema values, it first
tries the override dict

small cost of a dictionary being instantiated, if I make it none then each time I am also comparing to check if it is a dict

Look at weakref.weakrefdictionary, as a class variable? Still need to check each time
but now I don't have another var per instance..
"""

@define(slots=True)
class ValueBase():
    """Entity wrapper

    Attributes:
        name (str): The name of the value, used to fetch metadata from schema

    Notes:
        - `schema` is a class-level variable used internally to fetch metadata, pointing to schema.objects.entities
    """
    # ---- Library-internal, set once globally ----
    schema: ClassVar['Namespace']

    # ---- instance fields ----
    _name:str = field(repr=True, alias="_name")

    def __attrs_post_init__(self):
        self.name = self._name
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name):
        name = self.validate_object(new_name)
        self._name = name

    @property
    def str_name(self):
        return self._cached_fetch_object(self._name).value

    @property
    def display_name(self):
        """Human-readable display name from schema."""
        return self._cached_fetch_object(self._name).display_name

    @property
    def description(self):
        """Description of the entity from schema."""
        return self._cached_fetch_object(self._name).description
    
    @classmethod
    def validate_object(cls, to_validate:str) -> str:

        to_validate = str(to_validate)
        try:
            cls._cached_fetch_object(to_validate)
            return to_validate
        
        except KeyError:
            name = to_validate.lower().strip() # this may give issues for metadata or other areas if certain fields have the same name but with different capitalisation
            for key,val in cls.schema.items():
                if name == val.display_name.lower():
                    return key
            
            for key, val in cls.schema.items():
                if name == val.value.lower():
                    return key
            raise ValueError(f"Val: {val} is not a valid value for {cls.__name__}")

    @classmethod
    @lru_cache(maxsize=32)
    def _cached_fetch_object(cls, name:str) -> 'Namespace':
        """Fetch entity information from schema.objects

        Args:
            name (str): The entity name to use

        Returns:
            Namespace object with object metadata for given entity

        Raises:
            ValueError: If no matching entity is found.
        """
        obj = cls.schema.get(name)
        if obj is None:
            raise KeyError(f"no object found for key {name} in {cls.__name__}")
        
        return obj

@define(slots=True)#eq and hash false so we can compare if entities are the same by name only
class nameValueBase(ValueBase): #must beware of the hash = false, as "different" instances will hash to the same in sets and dictionaries
    """Entity wrapper

    Attributes:
        val (str): The value of the entity

    """
    # ---- instance fields ----
    _val:str = field(repr=True, alias="_val") 

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.val = self._val # Validate and set the initial value
        
    @property
    def str_name(self):
        return self._cached_fetch_object(self._name).name

    @property
    def val(self):
        """Public getter for the entity value."""
        return self._val
    
    @property
    def type(self):
        """Type of the entity from schema."""
        return self._cached_fetch_object(self._name).type
    
    @property
    def format(self):
        """Format of the entity from schema."""
        return self._cached_fetch_object(self._name).format
    
    @classmethod
    def validate_object(cls, to_validate:str) -> str:
        
        to_validate = str(to_validate)
        try:
            cls._cached_fetch_object(to_validate)
            return to_validate
        
        except KeyError:
            name = to_validate.lower().strip() # this may give issues for metadata or other areas if certain fields have the same name but with different capitalisation
            for key,val in cls.schema.items():
                if name == val.display_name.lower():
                    return key
            
            for key, val in cls.schema.items():
                if name == val.name.lower():
                    return key
                
            raise ValueError(f"Val: {val} is not a valid value for {cls.__name__}")

@define(slots=True)
class formats():
    schema:ClassVar['Namespace']

    @classmethod
    @lru_cache(maxsize=32)
    def get_pattern(cls, key):
        """Fetch format information from schema.objects.formats

        Args:
            key (str): The format name to use (as seen in formats, i.e. 'json' not 'JSON')

        Returns:
            regex pattern to verify given format

        Raises:
            ValueError: If no matching format is found.
        """
        try:
            pattern_info = cls.schema.get(key)
            pattern = re.compile(pattern_info.pattern)
        except KeyError as e:
            raise e

        return pattern

    @classmethod
    def check_pattern(cls, inp_type:str, val:str) -> bool:
        pattern = cls.get_pattern(inp_type)  # Ensure the format exists
        return bool(pattern.fullmatch(val))

@define(slots=True)
class Entity(nameValueBase):

    @nameValueBase.val.setter
    def val(self, new_val:str):
        """Validate and set a new entity value

        Args:
            new_val (str): New value to assign entitiy

        Raises:
            ValueError: If the value cannot be cast to int if format is index
            AssertionError: If the value is not among allowed enum values
            RuntimeError: If the entity format is not index or label
        """
        info = self._cached_fetch_object(self._name)
        # is only of type string, so ignore this for now
        # in the future can link it to objects.format and regex to assert the type

        #formats are index or label
        if not formats.check_pattern(info.format, new_val):
            raise ValueError(f"val: {new_val} is not of required format: {info.format}")
       
        enums = info.get("enum", None)
        if enums:
            assert new_val in enums, f"val for {self} must be one of {enums} not {new_val}"

        self._val = new_val

@define(slots=True)
class Column(nameValueBase):
    
    @nameValueBase.val.setter
    def val():
        pass

    @classmethod
    @lru_cache(maxsize=128) #many different values so allow for larger cache for this
    def _cached_fetch_object(cls, name: str):
        # Optionally delegate back to Base method if logic identical
        return super()._cached_fetch_object.__wrapped__(cls, name)

@define(slots=True)
class Metadata(nameValueBase):
    """Metadata is quite unique, mainly due to the 'items' attribute
    
    This basically allows for the value of one metadata field, to be an array, or dictionary of other metadata fields

    """


    
    @nameValueBase.val.setter
    def val(self, new_val):
        pass

    @classmethod
    @lru_cache(maxsize=256) #many different values so allow for larger cache for this
    def _cached_fetch_object(cls, name: str):
        # Optionally delegate back to Base method if logic identical
        return super()._cached_fetch_object.__wrapped__(cls, name)

@define(slots=True)
class Suffix(ValueBase):
    pass

@define(slots=True)
class Modalitiy():
    pass
    
@define(slots=True)
class raw_Datatype(ValueBase):
    pass


def _set_object_schemas(schema:'Namespace'):
    Entity.schema = schema.objects.entities
    Column.schema = schema.objects.columns
    Suffix.schema = schema.objects.suffixes
    Metadata.schema = schema.objects.metadata
    formats.schema = schema.objects.formats
    return

__all__ = ["Entity", "Column", "Metadata", "Suffix", "_set_object_schemas", "raw_Datatype"]