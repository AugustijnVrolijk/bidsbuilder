from attrs import define, field
from ..schema_objects import Entity, raw_Datatype, Suffix
from ...util.hooks import *

from abc import ABC, abstractmethod
from typing import Union, ClassVar, TYPE_CHECKING, Self, Optional, Type
from functools import lru_cache

if TYPE_CHECKING:
    from bidsschematools.types.namespace import Namespace
    from .dataset_tree import FileEntry, FileCollection, Directory

@define(slots=True)
class filenameBase(ABC):

    _tree_link:Union['FileEntry', 'FileCollection', 'Directory'] = field(init=False, default=None, repr=False, alias="_tree_link")

    @property
    @abstractmethod
    def name(self): ...

    @property
    @abstractmethod
    def local_name(self): ...

    @property #could consider caching, but parent can change, so need to then reset the cache
    def parent(self) -> 'filenameBase':
        if self._tree_link.parent:
            return self._tree_link.parent._name_link
        else: 
            None

    #def __setitem__(self):

    #def __getitem__(self):

@define(slots=True)
class agnosticFilename(filenameBase):
    
    _stem:str = field(repr=True, default='', alias="_stem")
    _valid_extensions:list[str] = field(repr=False, default=[], alias="_valid_extensions")
    _cur_ext:str = field(repr=True, default='', alias="_cur_ext")

    @property
    def name(self):
        return self._stem + self._cur_ext
    
    @property
    def local_name(self):
        return self.name

    def _change_ext(self, val:str):
        assert val in self._valid_extensions, f"extension {val} is not valid for {self}, choose on of {self._valid_extensions}"
        self._cur_ext = val

def _update_children_cback(instance:'CompositeFilename', tags:Union[str, list]=None):
    """
    Callback method which calls on self and all child instances to check their schema 
    add tags to specify which selectors to re-check
    """
    instance._tree_link.name = instance.local_name # change the name

    # no need to do: instance._file_link._check_schema - _iter_tree will yield the instance itself
    for child in instance._tree_link._iter_tree():
        child._file_link._check_schema(tags=tags)

@define(slots=True)
class CompositeFilename(filenameBase):
    """Base class for filename generation for files with entities

    Attributes:
        parent (Union[filenameBase, None]): Parent filename object to inherit from
        name (str): Name of the current filename component
    """
    schema: ClassVar[list] #should point to schema.rules.entities which is an ordered list
    entities: ClassVar[dict[str, Optional[Entity]]]
    suffix: ClassVar[Optional[Suffix]]
    datatype: ClassVar[Optional[raw_Datatype]]

    _entities: dict[str, Optional[Entity]] = field(factory=dict, repr=True, alias="_entities")
    _suffix: Optional[Suffix] = field(default=None, repr=True, alias="_suffix")
    _datatype: Optional[raw_Datatype] = field(default=None, repr=True, alias="_datatype")

    @classmethod
    def create(cls, entities:Optional[dict]=None, suffix:Optional[str]=None, datatype:Optional[str]=None):
        
        if entities:
            for key, val in entities.items():
                to_add = Entity(key, val)
                entities[key] = to_add

        if suffix:
            suffix = Suffix(suffix)

        if datatype:
            datatype = raw_Datatype(datatype)

        return cls(_entities=entities, _suffix=suffix, _datatype=datatype)

    @property
    def name(self) -> str:
        """Construct the full filename by combining parent names and current name."""
        return self._construct_name(self.entities, self.suffix, self.datatype)
    
    @property
    def local_name(self) -> str:
        """construct instance name from attributes unique to the instance."""
        return self._construct_name(self._entities, self._suffix, self._datatype)

    @classmethod
    def _construct_name(cls, n_entities:dict={}, n_suffix:Suffix=None, n_datatype:raw_Datatype=None, extension:str=None) -> str:
        
        ret_pairs = []
        for pos_entity in cls.schema:
            if (t_entity := n_entities.get(pos_entity, False)):
                ret_pairs.append(f"{t_entity.str_name}-{t_entity.val}") #str name is the correct display name for bids filenames
        entity_string = '_'.join(ret_pairs)

        if n_suffix is not None:
            entity_string += f"_{n_suffix.name}"
        elif n_datatype is not None:
            if entity_string:
                entity_string += f"_{n_datatype.name}"
            else:
                # for datatype folders, which are just the datatype
                entity_string = n_datatype.name

        if extension:
            entity_string += extension

        return entity_string

    @staticmethod
    def _name_validator(instance:'CompositeFilename', descriptor:'DescriptorProtocol', value:Union[str, Entity, Suffix, raw_Datatype]) -> Entity:
        
        tag_to_type: dict[str, Type[Entity]] = {
            "entities": Entity,
            "suffix": Suffix,
            "datatype": raw_Datatype,
        }

        match descriptor.tags:
            case "entities":
                cur_type = Entity
            case "suffix":
                cur_type = Suffix
            case "datatype":
                cur_type = raw_Datatype
            case _:
                raise RuntimeError("unrecognised entity for CompositeFilename _name_validator")
        
        if isinstance(value, cur_type):
            return value
        elif isinstance(value, str):
            return cur_type(value)
        else:
            raise TypeError(f"changing entities for {instance} requires either a string or {type(cur_type)} object") 
    
    @staticmethod
    def _suf_dtype_getter(instance:'CompositeFilename', descriptor:DescriptorProtocol,owner) -> Union[Suffix, raw_Datatype, None]:
        cur_val = getattr(instance, descriptor.name)
        if cur_val is not None:
            return cur_val
        elif instance.parent is not None and isinstance(instance.parent, Self):
            #descriptor_name = descriptor.name[1:] # strip the leading _ of descriptor.name
            return instance._suf_dtype_getter(instance.parent, descriptor, owner)
        else:
            return None

    suffix: ClassVar[Suffix] = HookedDescriptor(Suffix,fget=_suf_dtype_getter, fval=_name_validator,tags="suffix",callback=_update_children_cback)
    datatype: ClassVar[raw_Datatype] = HookedDescriptor(raw_Datatype,fget=_suf_dtype_getter,fval=_name_validator,tags="datatype",callback=_update_children_cback)
    entities: ClassVar[dict[str, Entity]] = HookedDescriptor(dict,fval=_name_validator,tags="entities",callback=_update_children_cback)

   

    @property
    def resolved_suffix(self) -> str: 
        """The current instance's suffix if specified, otherwise inherited from parent folders"""
        cur_val = self.suffix._name
        if cur_val is not None:
            return cur_val
        elif self.parent is not None:
            return self.parent.resolved_suffix
        else:
            return None
        
    @property
    def resolved_datatype(self) -> str: 
        """The current instance's datatype if specified, otherwise inherited from parent folders"""
        cur_val = self.datatype._name
        if cur_val is not None:
            return cur_val
        elif self.parent is not None:
            return self.parent.resolved_datatype
        else:
            return None
        
    @property
    def resolved_entities(self) -> dict:
        """The current instance's entities as well as those inherited from parents (i.e. session or subject)"""
        
        # can consider making this a seperate function and caching it depending on the input observableDict
        def _clean_entities() -> dict:
            clean_entities = dict()
            for key, value in self.entities.items():
                cat, val = value.level, value.val
                if val is not None:
                    clean_entities[key] = value
            return clean_entities

        if self.parent is None:
            cur_entities = dict()
        else:
            cur_entities = self.parent.resolved_entities

        cur_entities.update(_clean_entities()) # overwrite parent values with cur values
        return cur_entities
    
def _set_filenames_schema(schema:'Namespace'):
    CompositeFilename.schema = schema.rules.entities

__all__ = ["agnosticFilename", "CompositeFilename"]