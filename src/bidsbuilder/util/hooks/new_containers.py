import inspect
import types

from typing import TYPE_CHECKING, Union, Generator
from weakref import ReferenceType

from functools import wraps
from collections.abc import MutableMapping, MutableSequence, MutableSet
from abc import ABC


if TYPE_CHECKING:
    from .descriptors import DescriptorProtocol

class hookedContainerABC(ABC):

    forbidden_instance_names = {"_check_callback", "__observable_container_init__"}

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
    def __init__(self): self._data:dict = dict()
    def __getitem__(self, key): return self._data[key]
    def __setitem__(self, key, value): self._data[key] = value
    def __delitem__(self, key): del self._data[key]
    def __iter__(self): return iter(self._data)
    def __len__(self): return len(self._data)

class MinimalList(MutableSequence, DataMixin, hookedContainerABC):
    def __init__(self): self._data:list = list()
    def __getitem__(self, index): return self._data[index]
    def __setitem__(self, index, value): self._data[index] = value
    def __delitem__(self, index): del self._data[index]
    def __len__(self):  return len(self._data)
    def insert(self, index, value): self._data.insert(index, value)

class MinimalSet(MutableSet, DataMixin, hookedContainerABC):
    def __init__(self): self._data:set = set()
    def __contains__(self, value): return value in self._data
    def __iter__(self): return iter(self._data)
    def __len__(self): return len(self._data)
    def add(self, value): self._data.add(value)
    def discard(self, value): self._data.discard(value)

class ObservableType():
    def __observable_container_init__(self, descriptor:'DescriptorProtocol', weakref:ReferenceType):
        self._descriptor:'DescriptorProtocol' = descriptor
        self._ref:ReferenceType = weakref 
        self._frozen:bool = False

    def _check_callback(self):
        if not self._frozen:
            self._descriptor._trigger_callback(self._ref()) # weak reference so need to call it to access it


class create_dynamic_container():
    """
    create new type by mixing base_container with observableType

    decorate methods of new type

    set type class attributes, i.e. module scope as this file etc..
    """
    def __init__(self, base_container:Union[MinimalDict, MinimalList, MinimalSet], validator_flag) -> object:
        name = f"Observable{'Validator' if validator_flag else ''}{base_container.__name__}"
        self.base_container = base_container
        self.dynamic_container = types.new_class(name, tuple(base_container, ObservableType),kwds={})

        self.wrap_check_callback()
        self.wrap_frozen_check_callback()
        if validator_flag:
            self.wrap_validate_input()

        return self.dynamic_container

    def iter_methods_set(self, to_iter) -> Generator:
        for func_name in to_iter:
            if orig_method := getattr(self.dynamic_container, func_name, False):
                yield (orig_method, func_name)

    check_callback_methods = {"__setitem__", "__delitem__", "insert", "add", "discard"}

    def wrap_check_callback(self):
        
        for (orig_method, func_name)  in self.iter_methods_set(self.check_callback_methods):
            @wraps(orig_method)
            def _wrapped_check_callback(self:ObservableType, *args, **kwargs):
                orig_method(self, *args, **kwargs)
                self._check_callback()

            setattr(self.dynamic_container, func_name, _wrapped_check_callback)

    frozen_check_callback_methods = {"update", "extend"}

    def wrap_frozen_check_callback(self):
        for (orig_method, func_name)  in self.iter_methods_set(self.check_callback_methods):

            @wraps(orig_method)
            def _wrapped_frozen_check_callback(self:ObservableType, *args, **kwargs):
                self._frozen = True
                orig_method(self, *args, **kwargs)
                self._frozen = False
                self._check_callback()

            setattr(self.dynamic_container, func_name, _wrapped_frozen_check_callback)

    validate_input_methods = {"__setitem__", "insert", "add"}

    def wrap_validate_input(self):
        for (orig_method, func_name)  in self.iter_methods_set(self.check_callback_methods):

            @wraps(orig_method)
            def _wrapped_check_callback(self:ObservableType, *args, **kwargs):
                args = self._descriptor.fval(self._ref(), self._descriptor, *args, **kwargs)
                orig_method(self, *args, **kwargs)

            setattr(self.dynamic_container, func_name, _wrapped_check_callback)

_class_cache = {}

def make_proxying_init_for(base_init):
    sig = inspect.signature(base_init)
    def __init__(self, *args, **kwargs):
        bound = sig.bind(self, *args, **kwargs)
        base_init(*bound.args, **bound.kwargs)
        # no observable init here; we’ll inject post-init anyway
    return __init__

def make_dynamic(base, observable):
    def __init__(self, *args, **kwargs):
        # figure out what init belongs to the base
        base_init = base.__init__
        sig = inspect.signature(base_init)

        # bind args/kwargs to the base signature
        bound = sig.bind(self, *args, **kwargs)
        base_init(*bound.args, **bound.kwargs)

        # then inject observable state
        observable.__init__(self, descriptor=kwargs.get("descriptor"), weakref=kwargs.get("weakref"))

    return type(f"Observable{base.__name__}", (base, observable), {"__init__": __init__})

def wrap_container(original_container:object, descriptor:'DescriptorProtocol', instance_reference:ReferenceType, validator_flag:bool):

    wrapped_name = f"Observable{'Validator' if validator_flag else ''}{original_container.__name__}"

    observable_container = _class_cache.get(wrapped_name, False)
    if not observable_container:
        observable_container = create_dynamic_container(original_container, validator_flag)
        _class_cache[wrapped_name] = observable_container

    new_instance = observable_container(descriptor, instance_reference)
    if isinstance(new_instance, (MinimalDict, MinimalSet)):
        new_instance.update(original_container)
    elif isinstance(new_instance, MinimalList):
        new_instance.extend(original_container)

    """
    
    2. check cache for class (using name)
        2.1 if not present create class dynamically 

    3. create instance of cached class
        3.1 set descriptor, weakref, etc.. (either through closer, or by setting __init__)

    4. based on type, run update/extend etc.. to populate the instance

    return instance
    """
