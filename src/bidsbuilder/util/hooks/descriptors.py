from __future__ import annotations

import weakref
import types
from typing import Any, Callable, Generic, TypeVar, Union, overload, Self, TypedDict, Unpack, ClassVar
from functools import partial

from .containers import *
from .containers import ObservableType

VAL = TypeVar("VAL")
CBACK = TypeVar("Descriptor", bound="DescriptorProtocol")
INSTANCE = TypeVar("Instance", bound="object")
OWNER = TypeVar("Owner", bound="type")

class DescriptorProtocol(Generic[VAL]):
    """
    DescriptorProtocol is a protocol that defines the methods and attributes that a descriptor must implement.
    It is used to type hint the descriptor classes.
    This allows for better type checking and code completion in IDEs.
    """
    def __init__(self:Self, *, tags:Union[list, str, None]=None, **kwargs) -> None: ...
    def __set_name__(self:Self, owner:OWNER, name:str) -> None: ...
    name:str
    @overload    
    def __get__(self:Self, instance:INSTANCE, owner:OWNER) -> VAL: ...
    def __get__(self:Self, instance:None, owner:OWNER) -> Self: ...
    def __set__(self:Self, instance:INSTANCE, value:VAL) -> None: ...
    def _trigger_callback(self:Self, instance:INSTANCE) -> None: ...

class CallbackBase(Generic[VAL]): # generic base class to enable dynamic type hinting
    """
    Callback base allows for tags to be passed, moreover it also sets the name of the raw attribute
    to be the same as the name of the descriptor with an underscore, i.e. '_test' for 'test'

    this is used to support local data storage for slotted classes
    """
    def __init__(self, *, tags:Union[list, str, None]=None, default:Any=None, **kwargs) -> None:
        self.tags:Union[list, str, None] = tags
        self.variables: dict[int, Any] = {}
        self.default:Any = default
        super().__init__(**kwargs)

    def __set_name__(self, owner:OWNER, name:str) -> None:
        """add underscore for instance variable. All classes are slotted so cannot use
        __dict__. Consequently use '_' to denote the raw attribute and store it on the instance
        also makes debugging easier as the instance owns its attributes"""
        self.name:str = f"{name}"

    def _set_quiet(self, instance:INSTANCE, value:VAL) -> None:
        """sets the value without triggering callbacks"""
        self.variables[id(instance)] = value

class CallbackGetterMixin():
    """
    Mixin for descriptors that have a custom getter method which is given as a parameter

    i.e. for Suffix, Entity, or Datatype, where the custom getter can search parent instances
    if the current instance does not have the value set
    """
    def __init__(self, *, fget:Callable[[INSTANCE, CBACK, OWNER], VAL], **kwargs) -> None:
        self.fget:Callable[[INSTANCE, CBACK, OWNER], VAL] = fget
        super().__init__(**kwargs)

    def __get__(self, instance:INSTANCE, owner:OWNER) -> VAL:
        if instance is None:
            return self
        return self.fget(instance, self.variables.get(id(instance), self.default), self)
    
class CallbackNoGetterMixin():
    """
    Mixin for descriptors that do not have a getter method, i.e. they use the default getter
    """
    def __get__(self, instance:INSTANCE, owner:OWNER) -> VAL:
        if instance is None:
            return self
        return self.variables.get(id(instance), self.default)

class PerInstanceCallbackMixin():
    """
    Mixin for per-instance callbacks, i.e. each instance of the descriptor can have its own callback/callbacks

    Useful for attributes such as exists, enabling callback checking for other objects which depend on their 
    exists value. I.e. dataset_description is dependent on genetic_info existing.
    """
    def __init__(self, **kwargs) -> None:
        self.callbacks:dict[int, list] = {}
        self.finalizers:dict[int, Any] = {}
        super().__init__(**kwargs)

    def _trigger_callback(self, instance:INSTANCE) -> None:
        instance_id = id(instance)
        if (callbacks := self.callbacks.get(instance_id, False)):
            to_del = []
            for i, cback in enumerate(callbacks):
                method = cback()
                # need to unpack it as the callback is a weakref.WeakMethod
                # as such if the object that the method is linked to gets deleted (garbage collected)
                # the WeakMethod returns None rather than a callable method 
                if method:
                    method(tags=self.tags)
                else:
                    to_del.append(i)
            self._remove_callback(instance_id, to_del)

    def _remove_callback(self, instance_id:int, indices:list[int]) -> None:
        if not indices:
            return
        indices = sorted(indices, reverse=True) 
        cbacks:list = self.callbacks.get(instance_id)
        for i in indices:
            cbacks.pop(i)

        if not cbacks:
            self._remove(instance_id)

    def _remove(self, instance_id:int) -> None:
        self.callbacks.pop(instance_id)
        cur_finaliser:weakref.finalize = self.finalizers.pop(instance_id)
        cur_finaliser.detach()
        
    def add_callback(self, instance:INSTANCE, callback:Callable[[Union[list,str,None]],Any]) -> None:
        """
        Adds a callback (a class method) for this attribute of the given instance
        The callback will trigger when setting the attribute to a new value, appending or changing keys for lists and dictionaries as well

        This method will only work for class methods, if it is a regular function then it is not supported (can be done but need to use weakref.ref() instead)
        """
        weak_callback = weakref.WeakMethod(callback)
        instance_id = id(instance)
        self.callbacks.setdefault(instance_id, []).append(weak_callback)
        _del_callback = partial(self._remove, instance_id)
        if instance_id not in self.finalizers: # only needs to happen once, otherwise it may create duplicates if multiple callbacks are added
            self.finalizers[instance_id] = weakref.finalize(instance, _del_callback)

class SingleCallbackMixin():
    """
    Mixin for single callbacks, i.e. only one callback can be registered for this field 
    and is applied to all instances of the descriptor

    at the time of writing, this is used for the callbacks of "parent" attributes.
    i.e. Entity, Suffix, or datatype, where the single callback is defined to make each "child"
    and the parent itself check their schema / update their tree name reference
    """
    def __init__(self, *, callback:Callable[[INSTANCE, Union[list,str,None]], Any], **kwargs) -> None:
        self.callback:Callable[[INSTANCE, Union[list,str,None]], Any] = callback
        super().__init__(**kwargs)

    def _trigger_callback(self, instance:INSTANCE) -> None:
        self.callback(instance, self.tags)

def _make_container_mixin(_base_getter_cls:Union[CallbackNoGetterMixin, CallbackGetterMixin], validator:bool) -> type:
    """
    Mixin for descriptors that wrap a container type (list or dict)

    takes _base_getter_cls which defines whether the descriptor has a getter method or not
    as well as whether it has a validator method or not
    """
    class ContainerMixin(_base_getter_cls):
        TYPEIDX:ClassVar[bool] = False

        def __init__(self, type_hint:type, factory:Callable=None, **kwargs):
            if not isinstance(type_hint, type):
                raise TypeError(f"type_hint must be a type, got {type(type_hint)}")
            elif not is_supported_type(type_hint):
                raise TypeError(f"type_hint must be a supported container type (list, dict, set or MinimalList, MinimalDict, MinimalSet and any of their subclasses), got {type_hint}")
            
            self.type_hint:type = type_hint
            if factory is None:
                self.factory:type = type_hint
            else:
                self.factory:Callable = factory
            super().__init__(**kwargs)

        def _instantiate_default_(self, instance:INSTANCE) -> ObservableType:
            if self.factory == self.type_hint:
                observable_type = wrap_container(self.factory, self.TYPEIDX)
                default_instance = observable_type()
            else:
                default_instance = wrap_container(self.factory(instance, self), self.TYPEIDX)

            default_instance._observable_container_init_(self, weakref.ref(instance))
            return default_instance

        def __get__(self, instance:INSTANCE, owner:OWNER) -> VAL:
            if instance is None:
                return self
            if id(instance) not in self.variables:
                self.variables[id(instance)] = self._instantiate_default_(instance)
            return _base_getter_cls.__get__(self, instance, owner) # must return the observable type

        def __set__(self, instance:INSTANCE, value:VAL) -> None:
            """
            no repeated check when setting attributes
            assume types are static, i.e. no changing attribute from int to a list or dict
            """
            if type(value) != self.type_hint:
                raise TypeError(f"When setting {instance}.{self.name}, it must be a container of type {self.type_hint}")
            _observable_obj:ObservableType = wrap_container(value, self.TYPEIDX)
            _observable_obj._observable_container_init_(self, weakref.ref(instance))
            self.variables[id(instance)] = _observable_obj
            self._trigger_callback(instance)  
            """
            need to trigger callbacks since 05/09/2025. wrap_container just sets the __class__ to an observable type, so doesn't trigger callbacks
            like the old way
            """

    class ContainerValidatorMixin(ContainerMixin):
        TYPEIDX:ClassVar[bool] = True

        def __init__(self, *, fval:Callable[[INSTANCE, CBACK, Any], VAL], **kwargs):
            self.fval:Callable[[INSTANCE, CBACK, Any], VAL] = fval
            super().__init__(**kwargs)

    if validator:
        return ContainerValidatorMixin
    else:
       return ContainerMixin

class PlainMixin():
    """
    mixin for descriptors who's value is a plain value, i.e. str, or int, or float.
    """
    def __set__(self, instance:INSTANCE, value:VAL) -> None:
        self.variables[id(instance)] = value
        self._trigger_callback(instance)

class PlainValMixin():
    """
    mixin for descriptors who's value is a plain value, i.e. str, or int, or float, and includes a validator
    """
    def __init__(self, *, fval:Callable[[INSTANCE, CBACK, Any], VAL], **kwargs):
        self.fval:Callable[[INSTANCE, CBACK, Any], VAL]= fval
        super().__init__(**kwargs)

    def __set__(self, instance:INSTANCE, value:Any) -> None:
        n_value = self.fval(instance, self, value)
        self.variables[id(instance)] = n_value
        self._trigger_callback(instance)

_callback_types = {}

def _dynamic_callback_type(container:bool=False, single:bool=False, getter:bool=False, validator:bool=False) -> type[DescriptorProtocol[VAL]]: 
    assert isinstance(container, bool), f"container must be a boolean, got {type(container)}"
    assert isinstance(single, bool), f"single must be a boolean, got {type(single)}"

    key = (container, single, getter, validator)
    if key in _callback_types:
        return _callback_types[key]

    bases = [CallbackBase[VAL]]
    name = f"{'Single' if single else 'Multi'}Callback{'Container' if container else 'Field'}{'Getter' if getter else ''}{'Validator' if validator else ''}"

    if single:
        bases.append(SingleCallbackMixin)
    else:
        bases.append(PerInstanceCallbackMixin)

    if getter:
        getter_cls = CallbackGetterMixin
    else:
        getter_cls = CallbackNoGetterMixin

    if container:
        bases.append(_make_container_mixin(getter_cls, validator))
    else:
        bases.append(getter_cls)
        if validator:
            bases.append(PlainValMixin)
        else:
            bases.append(PlainMixin)

    # {"__module__": __name__}
    # it gives me an error if I try pass them as kwds={}...
    # so I just define it after...
    ret_callback_type = types.new_class(name, tuple(bases),kwds={})
    ret_callback_type.__module__ = __name__
    _callback_types[key] = ret_callback_type
    return ret_callback_type

# Define the callback kwargs type for type checking
class callbackKwargs(TypedDict, total=False):
    fget: Callable[[INSTANCE, VAL, CBACK], VAL]
    fval: Callable[[INSTANCE, CBACK, Any], VAL]
    tags: Union[list, str, None]
    callback: Callable[[INSTANCE, Union[list, str, None]], Any]
    factory: Callable[[INSTANCE, CBACK], Union[type, object]]
    default: Any

def HookedDescriptor(type_hint:type[VAL], **kwargs:Unpack[callbackKwargs]) -> DescriptorProtocol[VAL]:  
    assert isinstance(type_hint, type), f"type_hint must be a type, got {type(type_hint)}"

    single = "callback" in kwargs
    getter = "fget" in kwargs
    validator = "fval" in kwargs
    container = is_supported_type(type_hint)
    if container:
        kwargs["type_hint"] = type_hint

    cback_obj = _dynamic_callback_type(container=container, single=single, getter=getter,validator=validator)

    return cback_obj[type_hint](**kwargs)
