from attrs import define, field
from typing import Union, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace

@define(slots=True)
class Entity():
    """Entity wrapper

    Attributes:
        name (str): The entity of the animal
        val (str): The value of the entity

    Notes:
        - `schema` is a class-level variable used internally to fetch metadata, pointing to schema.objects.entities
    """
    # ---- Library-internal, set once globally ----
    schema: ClassVar['Namespace']

    # ---- instance fields ----
    name:str = field(repr=True)
    _val:str = field(repr=True, alias="_val")

    @property
    def display_name(self):
        """Human-readable display name from schema."""
        return self.fetch_object(self.name).display_name

    @property
    def description(self):
        """Description of the entity from schema."""
        return self.fetch_object(self.name).description
    
    @property
    def val(self):
        """Public getter for the entity value."""
        return self._val
    
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
    
    @staticmethod
    def fetch_object(name) -> 'Namespace':
        """Fetch entity information from schema.objects

        Args:
            name (str): The entity name to use (as seen in entities, i.e. 'ses' not 'session')

        Returns:
            Namespace object with object metadata for given entity

        Raises:
            ValueError: If no matching entity is found.
        """
        for entitity in Entity.schema.keys():
            if entitity.name == name:
                return entitity
        raise ValueError(f"no entitiy found for '{name}'")
