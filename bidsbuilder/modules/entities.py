import re

from attrs import define, field
from typing import Union, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class universalNameBase():
    """Entity wrapper

    Attributes:
        name (str): The entity of the animal

    Notes:
        - `schema` is a class-level variable used internally to fetch metadata, pointing to schema.objects.entities
    """
    # ---- Library-internal, set once globally ----
    schema: ClassVar['Namespace']

    # ---- instance fields ----
    name:str = field(repr=True)

    def __attrs_post_init__(self):
        try:
            self.fetch_object(self.name)
        except KeyError as e:
            raise KeyError(f"Entity {self.name} not found in schema") from e
    
    @property
    def display_name(self):
        """Human-readable display name from schema."""
        return self.fetch_object(self.name).display_name

    @property
    def description(self):
        """Description of the entity from schema."""
        return self.fetch_object(self.name).description
    
    @classmethod
    def fetch_object(cls, name) -> 'Namespace':
        """Fetch entity information from schema.objects

        Args:
            name (str): The entity name to use (as seen in entities, i.e. 'ses' not 'session')

        Returns:
            Namespace object with object metadata for given entity

        Raises:
            ValueError: If no matching entity is found.
        """
        for pos_obj in cls.schema.keys():
            if pos_obj.name == name:
                return pos_obj
        raise ValueError(f"no entitiy found for '{name}'")

@define(slots=True)
class nameValueBase(universalNameBase):
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
        except:
            raise NotImplementedError("Not yet finished error handling for nameBase __attrs_post_init__")
        
    @property
    def val(self):
        """Public getter for the entity value."""
        return self._val
    
    @property
    def type(self):
        """Type of the entity from schema."""
        return self.fetch_object(self.name).type
    
    
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
class columns(nameValueBase):
    
    @nameValueBase.val.setter
    def val():
        pass

@define(slots=True)
class metadata(nameValueBase):
    pass

@define(slots=True)
class suffixes(nameValueBase):
    pass

class formats():
    schema:ClassVar['Namespace']

    @classmethod
    def fetch_object(cls, name) -> 'Namespace':
        """Fetch format information from schema.objects.formats

        Args:
            name (str): The format name to use (as seen in formats, i.e. 'json' not 'JSON')

        Returns:
            Namespace object with object metadata for given format

        Raises:
            ValueError: If no matching format is found.
        """
        for pos_obj in cls.schema.keys():
            if pos_obj == name:
                return pos_obj
        raise ValueError(f"no format found for '{name}'")

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
class filenameBase:
    """Base class for filename generation

    Attributes:
        parent (Union[filenameBase, None]): Parent filename object to inherit from
        name (str): Name of the current filename component
    """
    parent: Union['filenameBase', None] = field(default=None, repr=False)
    _entities: dict = field(default=dict(),repr=True)
    _suffix: suffixes = field(default=None, repr=True)

    def __attrs_post_init__(self):
        if self.parent is not None and not isinstance(self.parent, filenameBase):
            raise TypeError("Parent must be an instance of filenameBase or None")

    @property
    def entities(self) -> dict:
        return 

    @property
    def suffix(self) -> Union[suffixes, None]:
        """Get the suffix for the filename."""
        return self._suffix

    @property
    def full_name(self) -> str:
        """Construct the full filename by combining parent names and current name."""
        if self.parent:
            return f"{self.parent.full_name}_{'_'.join(self.name)}"
        return '_'.join(self.name)

"""
Create filename class which composits from the above classes and dynamically creates filename from parent chain.

this can be imported into main file classes.








"""