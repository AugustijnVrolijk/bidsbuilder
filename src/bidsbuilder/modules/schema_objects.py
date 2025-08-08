import re

from attrs import define, field
from typing import Union, ClassVar, TYPE_CHECKING, Any
from functools import lru_cache
from weakref import WeakKeyDictionary

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
        """
        validate name, if it can't be found as a key tries against display name and value
        """
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
            raise ValueError(f"Val: {to_validate} is not a valid value for {cls.__name__}")

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

@define(slots=True)
class nameValueBase(ValueBase):
    """Entity wrapper

    Attributes:
        val (str): The value of the entity

    """
    

    _override: ClassVar[WeakKeyDictionary] = WeakKeyDictionary()

    # ---- instance fields ----
    _val:str = field(init=False, default=None, repr=True, alias="_val") 
    level:str = field(repr=True)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        #self.val = self._val # as of 08/08/2025: Users will not interact with any schema_objects themselves.
        # bidsbuilder will initiliase them as necessary as empty holders of necessary value / type (i.e. for entities or metadata)
        # with no val. Instead users will then assign 
        
    @level.validator
    def _check_level(self, attribute, value):
        level_types = ["required", "recommended", "optional"]
        if value not in level_types:
            raise ValueError(f"Value must be one of: {level_types}")

    valid_types:ClassVar = {
        "integer":int,
        "string":str,
        "number":float,
        "array":list,
        "object":dict,
    }

    @classmethod
    def _check_type(cls, inp_type:str, val:Any) -> bool:
        if (cor_type := cls.valid_types.get(inp_type, False)):
            return isinstance(val, cor_type)
        else:
            raise RuntimeError(f"given type: {inp_type} is not supported. Valid types include: {cls.valid_types.keys()}")

    @property
    def str_name(self):
        return self._cached_fetch_object(self._name).name

    @property
    def val(self):
        """Public getter for the entity value."""
        return self._val
    
    @staticmethod
    def _validate_number(is_correct:bool, new_val:Union[float, int], rules:'Namespace', error_msg:str) -> tuple[bool, str]:

        if max := rules.get("maximum", False):
            if not new_val <= max:
                is_correct = False
                error_msg += f"must be lesser than or equal to {max}\n"

        """ # I believe max and min value are only for suffix
        if max:=rules.get("maxValue", False):
            if not new_val <= max:
                is_correct = False
                error_msg += f"must be lesser than or equal to {max}\n"

        if min:=rules.get("minValue", False):
            if not new_val >= min:
                is_correct = False
                error_msg += f"must be greater than or equal to {min}\n"
        """

        if min:=rules.get("minimum", False):
            if not new_val >= min:
                is_correct = False
                error_msg += f"must be greater than or equal to {min}\n"

        if min:=rules.get("exclusiveMinimum", False):
            if not new_val > min:
                is_correct = False
                error_msg += f"must be greater than {min}\n"

        return (is_correct, error_msg)
    
    @staticmethod
    def _validate_string(is_correct:bool, new_val:str, rules:'Namespace', error_msg:str) -> tuple[bool, str]:

        if enums := rules.get("enum", None):
            if new_val not in enums:
                is_correct = False
                error_msg += f"must be one of {enums}\n"

        return (is_correct, error_msg)

    @staticmethod
    def _validate_array(is_correct:bool, new_val:list, rules:'Namespace', error_msg:str) -> tuple[bool, str]:
        
        if max:=rules.get("maxItems", False):
            if not len(new_val) <= max:
                is_correct = False
                error_msg += f"must have fewer items than {max}\n"

        if min:=rules.get("minItems", False):
            if not len(new_val) >= min:
                is_correct = False
                error_msg += f"must have more items than {min}\n"

        if item_rules := rules.get("items", False):
            error_msgs = set() # To ensure if we have large lists, that we don't get massive error messages printed
            # this will still have some duplicates, i.e. if item rules has multiple rules and one val failed 1, and the other failed
            # 2, including the one the first failed. But I can't be bothered to change the way error messages are propogated atm.
            is_sub_val_correct = True
            for val in new_val:
                t_is_correct, sub_val_error_msg = nameValueBase._validate_new_val(val, item_rules, error_msg="")
                is_sub_val_correct = (t_is_correct and is_sub_val_correct)
                error_msgs.add(sub_val_error_msg)

            if not is_sub_val_correct:
                error_msg += f"One or more items didn't adhere to:\n"
                for msg in error_msgs:
                    error_msg += msg

            is_correct = (is_correct and is_sub_val_correct)
            
        return (is_correct, error_msg)
    
    def _validate_object(self, is_correct:bool, new_val:dict, rules:'Namespace', error_msg:str) -> tuple[bool, str]:
        """
        keys include recommended, required, properties, and additionalProperties, previously had recommended_fields but this should be removed.         
        """
        # at the moment ignore recommended? Don't throw an error if they are left out... Should in the future edit to throw warnings
        # annoyingly 
        # will leave this as is for the moment
        # hopefully future bids will make properties able to be recursive.

        return (is_correct, error_msg)

    def _validate_new_val(self, new_val:Any, rules:'Namespace', error_msg:str) -> tuple[bool, str]:

        """handle anyOf recursion"""
        if all_rules := rules.get("anyOf", False):
            for ruleset in all_rules:
                is_correct, error_msg = self._validate_new_val(new_val, ruleset, error_msg=error_msg)
                if is_correct:
                    return (is_correct, error_msg)
                error_msg += "  OR  \n"
            return (False, error_msg[:-6]) #trim final OR

        is_correct = True
        if c_format:=rules.get("format", False):
            if not formats.check_pattern(c_format, new_val):
                error_msg += f"Incorrect format, should be: format.{c_format}\n"
                is_correct = False

        if c_type:=rules.get("type", False):
            if not self._check_type(c_type, new_val):
                error_msg += f"Incorrect Type. Should be: {c_type}\n"
                return False, error_msg # to protect against methods assuming correct type and throwing an error down the line
                                        # enables people to wrap setting value in a single try: ... except ValueError as e:

            if c_type in ["integer", "number"]:
                is_correct, error_msg = self._validate_number(is_correct, new_val, rules, error_msg)  
            elif c_type == "string":
                is_correct, error_msg = self._validate_string(is_correct, new_val, rules, error_msg)  
            elif c_type == "array":
                is_correct, error_msg = self._validate_array(is_correct, new_val, rules, error_msg)  
            elif c_type == "object":
                is_correct, error_msg = self._validate_object(is_correct, new_val, rules, error_msg)  
        else:
            raise RuntimeError(f"No type for {self}\nRules: {rules}")

        return (is_correct, error_msg)    

    @val.setter
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
        cur_overrides = self._override.get(self, {})
        info.update(cur_overrides)

        orig_msg = f"Value: {new_val} for {self.name} is not valid:\n"
        is_correct, error_msg = self._validate_new_val(new_val, info, orig_msg)

        if not is_correct:
            raise ValueError(error_msg)
        else:
            self._val = new_val

    def __getitem__(self, key):
        assert isinstance(self._val, dict)
        return self._val[key]

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

@define(slots=True, weakref_slot=True, hash=True)
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
        cur_overrides = self._override.get(self, {})
        info.update(cur_overrides)

        if not formats.check_pattern(info['format'], new_val):
            raise ValueError(f"val: {new_val} is not of required format: {info.format}")
       
        if enums := info.get("enum", None):
            assert new_val in enums, f"val for {self} must be one of {enums} not {new_val}"

        self._val = new_val

@define(slots=True)
class Column(nameValueBase):
    
    @nameValueBase.val.setter
    def val():
        pass

    @classmethod
    @lru_cache(maxsize=256) #many different values so allow for larger cache for this
    def _cached_fetch_object(cls, name: str):
        # Optionally delegate back to Base method if logic identical
        return super()._cached_fetch_object.__wrapped__(cls, name)

@define(slots=True, weakref_slot=True, hash=True)
class Metadata(nameValueBase):
    """Metadata is quite unique, mainly due to the 'items'/'properties' attribute 
    
    This basically allows for the value of one metadata field, to be an array, or dictionary of other metadata fields

    """
    
    @nameValueBase.val.setter
    def val(self, new_val):
        self._val = new_val

        info:'Namespace' = self._cached_fetch_object(self._name)
        cur_overrides = self._override.get(self, {})
        info.update(cur_overrides)

    @classmethod
    @lru_cache(maxsize=256) # many different values so allow for larger cache for this
    def _cached_fetch_object(cls, name: str):
        obj = cls.schema.get(name) # admittedly don't really need a cache as Namespace.get is already hashed and fast...
        if obj is None:
            raise KeyError(f"no object found for key {name} in {cls.__name__}")
        
        return obj

@define(slots=True)
class Suffix(ValueBase):
    pass

@define(slots=True)
class Modalitiy():
    pass
    
@define(slots=True)
class raw_Datatype(ValueBase):
    pass

@define(slots=True)
class extensions(ValueBase):
    pass

def _set_object_schemas(schema:'Namespace'):
    Entity.schema = schema.objects.entities
    Column.schema = schema.objects.columns
    Suffix.schema = schema.objects.suffixes
    Metadata.schema = schema.objects.metadata
    formats.schema = schema.objects.formats
    extensions.schema = schema.objects.extensions

    return

__all__ = ["Entity", "Column", "Metadata", "Suffix", "_set_object_schemas", "raw_Datatype"]