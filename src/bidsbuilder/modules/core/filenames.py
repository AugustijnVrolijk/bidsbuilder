from attrs import define, field
from ..schema_objects import *

from typing import Union, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace
    from .dataset_tree import FileEntry

@define(slots=True)
class filenameBase():

    _tree_link:'FileEntry' = field(init=False, default=None, repr=False, alias="_tree_link")

    @property
    def name(self):
        raise NotImplementedError(f"Base class {type(self)} has no name")

    @property #could consider caching, but parent can change, so need to then reset the cache
    def parent(self):
        if self._tree_link:
            return self._tree_link.parent._name_link
        else: 
            None

@define(slots=True)
class agnosticFilename(filenameBase):
    
    _stem:str = field(repr=True, default='', alias="_stem")
    _valid_extensions:list[str] = field(repr=False, default=[], alias="_valid_extensions")
    _cur_ext:str = field(repr=True, default='', alias="_cur_ext")

    @property
    def name(self):
        return self._stem + self._cur_ext
    
    def _change_ext(self, val:str):
        assert val in self._valid_extensions, f"extension {val} is not valid for {self}, choose on of {self._valid_extensions}"
        self._cur_ext = val

@define(slots=True)
class CompositeFilename(filenameBase):
    """Base class for filename generation for files with entities

    Attributes:
        parent (Union[filenameBase, None]): Parent filename object to inherit from
        name (str): Name of the current filename component
    """
    schema: ClassVar['list'] #should point to schema.rules.entities which is an ordered list

    _entities: dict[Entity] = field(default=dict(), repr=True, alias="_entities")
    _suffix: Union['Suffix', None] = field(default=None, repr=True, alias="_suffix")
    _datatype: Union['raw_Datatype', None] = field(default=None, repr=True, alias="_datatype")

    @property
    def name(self) -> str:
        """Construct the full filename by combining parent names and current name."""
        cur_entities:dict[Entity] = self.entities
        
        ret_pairs = []
        for pos_entity in self.schema:
            t_entity:Entity = cur_entities.get(pos_entity, False)
            if t_entity:
                ret_pairs.append(f"{t_entity.str_name}-{t_entity.val}") #str name is the correct display name for bids filenames
        
        entity_string = '_'.join(ret_pairs)
        if self.suffix is not None:
            entity_string += f"_{self.suffix.name}"

        return entity_string

    @property
    def entities(self) -> dict:
        if self.parent is None:
            cur_entities = dict()
        else:
            cur_entities = self.parent.entities
        
        cur_entities.update(self._entities) #overwrite parent values with cur values
        return cur_entities
    
    @property
    def suffix(self) -> Union[Suffix, None]:
        
        if self._suffix is not None:
            return self._suffix
        elif self.parent is not None:
            return self.parent.suffix
        else:
            return None

    @property
    def datatype(self) -> Union[raw_Datatype, None]:
        if self._datatype is not None:
            return self._datatype
        elif self.parent is not None:
            return self.parent._datatype
        else:
            return None
    
    def update(self, key:str, val:str):
        #local entities only
        
        cor_ent:Entity = self._entities.pop(key, None)
        if cor_ent is not None:
            cor_ent.val = val
        elif key.lower().strip() == "suffix":
            self.suffix.name = val
        elif key.lower().strip() == "datatype":
            self.datatype.name = val
        else:
            raise KeyError(f"key: {key} was not found for {self}")
        
def _set_filenames_schema(schema:'Namespace'):
    CompositeFilename.schema = schema.rules.entities




