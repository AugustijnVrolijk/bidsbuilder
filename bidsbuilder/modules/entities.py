import re

from attrs import define, field
from typing import Union, ClassVar, TYPE_CHECKING
from functools import lru_cache

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace

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
        try:
            self.fetch_object(self.name)
        except KeyError as e:
            raise e
    
    @property
    def name(self):
        return self._name

    @property
    def display_name(self):
        """Human-readable display name from schema."""
        return self.fetch_object(self.name).display_name

    @property
    def description(self):
        """Description of the entity from schema."""
        return self.fetch_object(self.name).description
    
    @classmethod
    def fetch_object(cls, name:str) -> 'Namespace':
        """Fetch entity information from schema.objects

        Args:
            name (str): The entity name to use (as seen in entities, i.e. 'ses' not 'session')

        Returns:
            Namespace object with object metadata for given entity

        Raises:
            ValueError: If no matching entity is found.
        """
        obj = cls.schema.get(name)
        if obj is None:

            #try look if user provided display name or other name
            name = name.lower() # this may give issues for metadata or other areas if certain fields have the same name but with different capitalisation
            for key,val in cls.schema.items():
                if name == val.display_name.lower():
                    return cls.schema.get(key)
            
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

        try:
            self.val = self._val  # Validate and set the initial value
        except Exception as e:
            raise e
        
    @property
    def val(self):
        """Public getter for the entity value."""
        return self._val
    
    @property
    def type(self):
        """Type of the entity from schema."""
        return self.fetch_object(self.name).type
    
    @property
    def format(self):
        """Format of the entity from schema."""
        return self.fetch_object(self.name).format
    
    @classmethod
    def fetch_object(self, name):
        try:
            return super().fetch_object(name)
        except Exception as e:

            name = name.lower() # this may give issues for metadata or other areas if certain fields have the same name but with different capitalisation
            for key,val in self.schema.items():
                if name == val.name.lower():
                    self.name = key
                    return self.schema.get(key)

            raise e

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
        info = self.fetch_object(self.name)
        # is only of type string, so ignore this for now
        # in the future can link it to objects.format and regex to assert the type

        #formats are index or label
        if info.format == "index":
            try:
                int(new_val)
            except:
                raise ValueError(f"Expected value convertable to an int for entity {self} not {new_val}")
        elif info.format != "label":
            raise RuntimeError(f"Schema gave an unexpected format {info.format} for entity: {self}")

        enums = info.get("enum", None)
        if enums:
            assert new_val in enums, f"val for {self} must be one of {enums} not {new_val}"

        self._val = new_val

@define(slots=True)
class Column(nameValueBase):
    
    @nameValueBase.val.setter
    def val():
        pass

@define(slots=True)
class Metadata(nameValueBase):
    pass

@define(slots=True)
class Suffix(ValueBase):
    pass

class formats():
    schema:ClassVar['Namespace']

    @classmethod
    @lru_cache
    def get_pattern(cls, key) -> str:
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
            re.compile()
        except KeyError as e:
            raise e

        for pos_obj in cls.schema.keys():
            if pos_obj == key:
                return cls.schema[pos_obj].pattern
            
        raise ValueError(f"no format found for '{key}'")

    @classmethod
    def format_checker(cls, inp_type:str, val:str) -> bool:
        format = cls.fetch_object(inp_type)  # Ensure the format exists



"""
 objects.formats
        specifies regex to enforce the correct "format", this is useful as it can check for
        stuff like specific files etc...

        implement a lightweight function or class like selectorParser, but format_checker or something
        to check it. Can be called from columns, suffixes, metadata, entities etc.. and returns a boolean
        to see if val respects the given format

    objects.suffixes
        similar to entities, need to check for unit, max min, anyOf etc..

    object.columns
        similar to entities need to enforce format, unit, enum, max, min etc..

    objects.metadata
        similar to entities need to enforce format, enum, max min etc... 

    objects.entities
        need to fetch format and enum
        enforce if it is a "label" or "index", and if its enum enforce the possible types...

"""

@define(slots=True)
class CompositeFilename:
    """Base class for filename generation

    Attributes:
        parent (Union[filenameBase, None]): Parent filename object to inherit from
        name (str): Name of the current filename component
    """
    schema: ClassVar['Namespace'] #should point to schema.rules.entities

    parent: Union['CompositeFilename', None] = field(default=None, repr=False)
    _entities: dict[Entity] = field(default=dict(),repr=True)
    suffix: Union['Suffix', None] = field(default=None, repr=True)

    @property
    def entities(self) -> dict:
        if self.parent is None:
            cur_entities = dict()
        else:
            cur_entities = self.parent.entities
        
        cur_entities.update(self._entities) #overwrite parent values with cur values
        return cur_entities
    
    @property
    def name(self) -> str:
        """Construct the full filename by combining parent names and current name."""
        cur_entities:dict[Entity] = self.entities
        
        ret_pairs = []
        for pos_entity in self.schema.keys():
            t_entity:Entity = cur_entities.get(pos_entity, False)
            if t_entity:
                ret_pairs.append(f"{t_entity.name}-{t_entity.val}")
        
        entity_string = '_'.join(ret_pairs)
        if self.suffix:
            entity_string += f"_{self.suffix.name}"

        return entity_string

"""
Create filename class which composits from the above classes and dynamically creates filename from parent chain.

this can be imported into main file classes.


"""

__all__ = ["CompositeFilename","Entity", "Column", "Metadata", "Suffix"]