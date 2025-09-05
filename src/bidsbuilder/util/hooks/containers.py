import types

from typing import TYPE_CHECKING, Union, Generator, Type
from weakref import ReferenceType

from functools import wraps
from collections.abc import MutableMapping, MutableSequence, MutableSet
from abc import ABC

if TYPE_CHECKING:
    from .descriptors import DescriptorProtocol

class hookedContainerABC(ABC):
    """
    ABC class ensuring that users inheriting from base
    """
    forbidden_instance_names = {"__check_callback__", "__observable_container_init__"}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name in cls.forbidden_instance_names:
            if name in cls.__dict__:
                raise TypeError(
                    f"Class {cls.__name__} must not define `{name}`"
                )

class DataMixin():
    def __repr__(self): return f"{self.__class__.__name__}({repr(self._data)})"
    def __str__(self): return str(self._data)
    def __eq__(self, other): return self._data == getattr(other, '_data', other)
    def __ne__(self, other): return self._data != getattr(other, '_data', other)
    def __lt__(self, other): return self._data < getattr(other, '_data', other)
    def __le__(self, other): return self._data <= getattr(other, '_data', other)
    def __gt__(self, other): return self._data > getattr(other, '_data', other)
    def __ge__(self, other): return self._data >= getattr(other, '_data', other)
    
class MinimalDict(MutableMapping, DataMixin, hookedContainerABC):
    def __init__(self, *args, **kwargs): self._data:dict = dict(*args, **kwargs)
    def __getitem__(self, key): return self._data[key]
    def __setitem__(self, key, value): self._data[key] = value
    def __delitem__(self, key): del self._data[key]
    def __iter__(self): return iter(self._data)
    def __len__(self): return len(self._data)

class MinimalList(MutableSequence, DataMixin, hookedContainerABC):
    def __init__(self, *args, **kwargs): self._data:list = list(*args, **kwargs)
    def __getitem__(self, index): return self._data[index]
    def __setitem__(self, index, value): self._data[index] = value
    def __delitem__(self, index): del self._data[index]
    def __len__(self):  return len(self._data)
    def insert(self, index, value): self._data.insert(index, value)

class MinimalSet(MutableSet, DataMixin, hookedContainerABC):
    def __init__(self, *args, **kwargs): self._data:set = set(*args, **kwargs)
    def __contains__(self, value): return value in self._data
    def __iter__(self): return iter(self._data)
    def __len__(self): return len(self._data)
    def add(self, value): self._data.add(value)
    def discard(self, value): self._data.discard(value)

def _make_observable(base_list:type):
    class ObservableList(base_list):
        __slots__ = ("_descriptor_", "_object_ref_", "_frozen_flag_")

        def __setitem__(self, *args, **kwargs):
            super().__setitem__(*args, **kwargs)
            self.__check_callback__()
        

    return ObservableList

class ObservableType():

    __slots__ = ("_descriptor_", "_object_ref_", "_frozen_flag_")
    def __observable_container_init__(self, descriptor:'DescriptorProtocol', weakref:ReferenceType):
        for n in self.__slots__:
            if getattr(self, n, False):
                raise TypeError(f"Observable objects reserve the attribute name: {n}\n Please rename this attribute to something else")

        setattr(self, self.__slots__[0], descriptor)
        setattr(self, self.__slots__[1], weakref)
        setattr(self, self.__slots__[2], False)

    def __check_callback__(self):
        if not self._frozen_flag_:
            self._descriptor_._trigger_callback(self._object_ref_()) # weak reference so need to call it to access it

class create_dynamic_container():
    """
    create new type by mixing base_container with observableType

    decorate methods of new type

    set type class attributes, i.e. module scope as this file etc..
    """
    def __init__(self, base_container:Union[MinimalDict, MinimalList, MinimalSet], validator_flag):
        name = f"Observable{'Validator' if validator_flag else ''}{base_container.__name__}"
        self.base_container = base_container
        self.dynamic_container = types.new_class(name, (base_container, ObservableType),kwds={})
        self.validator_flag = validator_flag

    def create(self) -> ObservableType:

        for (orig_method, func_name)  in self.iter_methods_set(self.check_callback_methods):
            setattr(self.dynamic_container, func_name, self.wrap_check_callback(orig_method))

        for (orig_method, func_name)  in self.iter_methods_set(self.frozen_check_callback_methods):
            setattr(self.dynamic_container, func_name, self.wrap_frozen_check_callback(orig_method))

        if self.validator_flag:
            self.wrap_with_validator()
            
        return self.dynamic_container

    def wrap_with_validator(self):
        for (orig_method, func_name)  in self.iter_methods_set(self.validate_input_methods):
            setattr(self.dynamic_container, func_name, self.wrap_validate_input(orig_method))

        _validator_init_name_ = "__observable_container_init__"
        _validator_init_ = getattr(self.dynamic_container, _validator_init_name_)
        setattr(self.dynamic_container, _validator_init_name_, self.wrap_validate_instance_creation(_validator_init_))

    def iter_methods_set(self, to_iter) -> Generator:
        for func_name in to_iter:
            if orig_method := getattr(self.dynamic_container, func_name, False):
                yield (orig_method, func_name)

    check_callback_methods = ("__setitem__", "__delitem__", "insert", "add", "discard")
    frozen_check_callback_methods = ("update", "extend")
    validate_input_methods = ("__setitem__", "insert", "add")

    @staticmethod
    def wrap_check_callback(orig_method):
        @wraps(orig_method)
        def _wrapped(self:ObservableType, *args, **kwargs):
            orig_method(self, *args, **kwargs)
            self.__check_callback__()
        return _wrapped

    @staticmethod
    def wrap_frozen_check_callback(orig_method):
        @wraps(orig_method)
        def _wrapped(self:ObservableType, *args, **kwargs):
            self._frozen_flag_ = True
            orig_method(self, *args, **kwargs)
            self._frozen_flag_ = False
            self.__check_callback__()
        return _wrapped

    @staticmethod
    def wrap_validate_input(orig_method):  
        @wraps(orig_method)
        def _wrapped(self:ObservableType, *args, **kwargs):
            n_args = self._descriptor_.fval(self._object_ref_(), self._descriptor_, *args, **kwargs)
            orig_method(self, *n_args, **kwargs)
        return _wrapped
    
    @staticmethod
    def wrap_validate_instance_creation(orig_method):

        @wraps(orig_method)
        def _wrapped(self:ObservableType, *args, **kwargs):
            orig_method(self, *args, **kwargs)
            
            self._frozen_flag_ = True

            if isinstance(self, MinimalList):
                 for i in range(len(self)):
                    self[i] = self[i]
            elif isinstance(self, MinimalDict):
                vals = [k for k in self]
                for key in vals:
                    val = self.pop(key)
                    self[key] = val
            elif isinstance(self, MinimalSet):
                vals = [item for item in self]
                for val in vals:
                    self.remove(val)
                    self.add(val)
            else:
                raise NotImplementedError(f"Validator wrapping not implemented for {self.__class__}")
        
            self._frozen_flag_ = False

        return _wrapped

_class_cache:dict[str, ObservableType] = {}

def is_supported_type(tp:Union[type, object]) -> bool:

    if not isinstance(tp, type):
        tp = tp.__class__

    if tp in (list, dict, set):
        return True
    if issubclass(tp, (MinimalList, MinimalDict, MinimalSet)):
        return True

    return False

def get_upgraded_container(og_container_type:Type, validator_flag:bool) -> ObservableType:

    wrapped_name = f"Observable{'Validator' if validator_flag else ''}{og_container_type.__name__}"

    observable_container = _class_cache.get(wrapped_name, False)
    if not observable_container:
        creator = create_dynamic_container(og_container_type, validator_flag)
        observable_container = creator.create()
        _class_cache[wrapped_name] = observable_container

    return observable_container

def wrap_container(container:Union[type, object], validator_flag:bool=False) -> Union[type[ObservableType], ObservableType]:
    """
    converts a container into an observable equivalent.
        - If container is a type, this will return an observable equivalent type

        - If container is an instance, this will return the upgraded observable instance
    """

    if isinstance(container, type):
        IS_TYPE = True
        og_type = container
    else:
        IS_TYPE = False
        og_container_contents = container
        og_type = container.__class__

    if not is_supported_type(og_type):
        raise TypeError(f"Only list, dict, set, their minimal equivalents and subclasses of the minimal equivalents are valid to be made observable, not {og_type}")

    core:dict[type, type] = {list:MinimalList, set:MinimalSet, dict:MinimalDict}

    # convert from python inbuilt types to MinimalType
    if og_type in core.keys():
        og_type = core[og_type]
        if not IS_TYPE:
            og_container_contents = og_type(og_container_contents) # initialise MinimalType with the original DS

    observable_container = get_upgraded_container(og_type, validator_flag)

    # return observable type, or upcast instance
    if IS_TYPE:
        return observable_container
    else:
        og_container_contents.__class__ = observable_container
        return og_container_contents

__all__ = ["wrap_container", "is_supported_type", "MinimalDict", "MinimalList", "MinimalSet"]