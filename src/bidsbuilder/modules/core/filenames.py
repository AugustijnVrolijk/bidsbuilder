from attrs import define, field
from ..schema_objects import *
from ...schema.callback_property import singleCallbackField, wrap_callback_fields

from typing import Union, ClassVar, TYPE_CHECKING


if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace
    from .dataset_tree import FileEntry, FileCollection, Directory

@define(slots=True)
class filenameBase():

    _tree_link:Union['FileEntry', 'FileCollection', 'Directory'] = field(init=False, default=None, repr=False, alias="_tree_link")

    @property
    def name(self):
        raise NotImplementedError(f"Base class {type(self)} has no name")

    @property #could consider caching, but parent can change, so need to then reset the cache
    def parent(self) -> 'filenameBase':
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

def _update_children_cback(instance:'CompositeFilename', tags:Union[str, list]=None):
    """
    Callback method which calls on self and all child instances to check their schema 
    add tags to specify which selectors to re-check
    """
    for child in instance._tree_link._iter_tree():
        child._file_link._check_schema(tags=tags)
    return

@define(slots=True)
class CompositeFilename(filenameBase):
    """Base class for filename generation for files with entities

    Attributes:
        parent (Union[filenameBase, None]): Parent filename object to inherit from
        name (str): Name of the current filename component
    """
    schema: ClassVar['list'] #should point to schema.rules.entities which is an ordered list
    entities: ClassVar[dict]
    suffix: ClassVar[Union[Suffix, None]]
    datatype: ClassVar[Union[raw_Datatype, None]]

    _entities: dict[Entity] = field(factory=dict, repr=True, alias="_entities")
    _suffix: Union['Suffix', None] = field(default=None, repr=True, alias="_suffix")
    _datatype: Union['raw_Datatype', None] = field(default=None, repr=True, alias="_datatype")

    def __attrs_post_init__(self):
        wrap_callback_fields(self)

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

    @staticmethod
    def _entities_getter(instance:'CompositeFilename', descriptor:singleCallbackField, owner:'CompositeFilename') -> dict:
        if instance.parent is None:
            cur_entities = dict()
        else:
            cur_entities = instance.parent.entities
        
        cur_entities.update(instance.entities) #overwrite parent values with cur values
        return cur_entities
    
    entities: ClassVar[dict] = singleCallbackField(fget=_entities_getter,tags="entities",callback=_update_children_cback)

    @staticmethod
    def _suffix_datatype_getter(instance:'CompositeFilename', descriptor:singleCallbackField, owner:'CompositeFilename') -> Union[Suffix, raw_Datatype,None]:
        cur_val = getattr(instance, descriptor.name)
        if cur_val is not None:
            return cur_val
        elif instance.parent is not None:
            return getattr(instance.parent, descriptor.name[1:])
        else:
            return None

    suffix: ClassVar = singleCallbackField(fget=_suffix_datatype_getter, tags="suffix",callback=_update_children_cback)
    datatype: ClassVar = singleCallbackField(fget=_suffix_datatype_getter, tags="datatype",callback=_update_children_cback)
    
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




