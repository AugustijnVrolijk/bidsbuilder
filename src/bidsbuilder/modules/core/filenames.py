from attrs import define, field
from ..schema_objects import Entity, raw_Datatype, Suffix
from ...util.reactive import singleCallbackField, wrap_callback_fields

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
        if self._tree_link.parent:
            return self._tree_link.parent._name_link
        else: 
            None

    def __setitem__(self):
        ...

    def __getitem__(self):
        ...

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
    instance._tree_link.name = instance.local_name
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
    _suffix: Union[Suffix, None] = field(default=None, repr=True, alias="_suffix")
    _datatype: Union[raw_Datatype, None] = field(default=None, repr=True, alias="_datatype")

    def __attrs_post_init__(self):
        wrap_callback_fields(self)

    @classmethod
    def create(cls, entities:Union[dict, None]=None, suffix:Union[str, None]=None, datatype:Union[str, None]=None):
        
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
    def _entities_getter(instance:'CompositeFilename', descriptor:singleCallbackField, owner:'CompositeFilename') -> dict:
        if instance.parent is None:
            cur_entities = dict()
        else:
            cur_entities = instance.parent.entities
        
        cur_entities.update(instance._entities) #overwrite parent values with cur values
        return cur_entities

    @staticmethod
    def _name_validator(instance:'CompositeFilename', descriptor:singleCallbackField, value:Union[str, Entity]) -> Entity:
        
        match descriptor.tags:
            case "entities":
                cur_type = Entity
            case "suffix":
                cur_type = Suffix
            case "datatype":
                cur_type = raw_Datatype
            case _:
                raise RuntimeError("unrecognised entity for entities name validator")
        
        if isinstance(value, cur_type):
            return value
        elif isinstance(value, str):
            return cur_type(value)
        else:
            raise TypeError(f"changing entities for {instance} requires either a string or {type(cur_type)} object") 
        
    entities: ClassVar[dict] = singleCallbackField(fget=_entities_getter,fval=_name_validator,tags="entities",callback=_update_children_cback)

    @staticmethod
    def _suffix_datatype_getter(instance:'CompositeFilename', descriptor:singleCallbackField, owner:'CompositeFilename') -> Union[Suffix, raw_Datatype,None]:
        cur_val = getattr(instance, descriptor.name)
        if cur_val is not None:
            return cur_val
        elif instance.parent is not None:
            return getattr(instance.parent, descriptor.name[1:])
        else:
            return None

    suffix: ClassVar = singleCallbackField(fget=_suffix_datatype_getter,fval=_name_validator,tags="suffix",callback=_update_children_cback)
    datatype: ClassVar = singleCallbackField(fget=_suffix_datatype_getter,fval=_name_validator,tags="datatype",callback=_update_children_cback)
    
    """
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
    """
    
def _set_filenames_schema(schema:'Namespace'):
    CompositeFilename.schema = schema.rules.entities




