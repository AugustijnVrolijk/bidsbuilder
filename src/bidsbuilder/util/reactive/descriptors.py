import weakref

import types

from typing import Any, Callable, Generic, TypeVar, Union, overload, Self
from functools import partial
from .containers import ObservableList, ObservableDict

VAL = TypeVar("VAL")
CBACK = TypeVar("Descriptor", bound="DescriptorProtocol")
INSTANCE = TypeVar("Instance", bound="object")
OWNER = TypeVar("Owner", bound="type")

def _do_nothing(instance:INSTANCE, descriptor:CBACK, value:Any) -> VAL:   
    return value

class DescriptorProtocol(Generic[VAL]):
    def __init__(self:Self, *, tags:Union[list, str, None]=None, **kwargs) -> None: ...
    def __set_name__(self:Self, owner:OWNER, name:str) -> None: ...
    @overload    
    def __get__(self:Self, instance:INSTANCE, owner:OWNER) -> VAL: ...
    def __get__(self:Self, instance:None, owner:OWNER) -> Self: ...
    def __set__(self:Self, instance:INSTANCE, value:VAL) -> None: ...

class CallbackBase(Generic[VAL]):
    def __init__(self, *, tags:Union[list, str, None]=None, **kwargs) -> None:
        self.tags:Union[list, str, None] = tags
        super().__init__(**kwargs)

    def __set_name__(self, owner:OWNER, name:str) -> None:
        """add underscore for instance variable. All classes are slotted so cannot use
        __dict__. Consequently use '_' to denote the raw attribute and store it on the instance
        also makes debugging easier as the instance owns its attributes"""
        self.name:str = f"_{name}"

class CallbackGetterMixin():
    """
    Mixin for descriptors that have a custom getter method which is given as a parameter

    i.e. for Suffix, Entity, or Datatype, where the custom getter can search parent instances
    if the current instance does not have the value set
    """
    def __init__(self, *, fget:Callable[[CBACK, INSTANCE, OWNER], VAL], **kwargs) -> None:
        self.fget:Callable[[CBACK, INSTANCE, OWNER], VAL] = fget
        super().__init__(**kwargs)

    def __get__(self, instance:INSTANCE, owner:OWNER) -> VAL:
        if instance is None:
            return self
        return self.fget(instance, self, owner)
    
class CallbackNoGetterMixin():
    """
    Mixin for descriptors that do not have a getter method, i.e. they use the default getter
    """
    def __get__(self, instance:INSTANCE, owner:OWNER) -> VAL:
        if instance is None:
            return self
        return getattr(instance, self.name)

class PerInstanceCallbackMixin():
    """
    Mixin for per-instance callbacks, i.e. each instance of the descriptor can have its own callback/callbacks

    Useful for attributes such as exists, enabling callback checking for other objects which depend on their 
    exists value. I.e. dataset_description is dependent on genetic_info existing.
    """
    def __init__(self, **kwargs) -> None:
        self.callbacks:dict[str, list] = {}
        self.finalizers:dict[str, Any] = {}
        super().__init__(**kwargs)

    def _trigger_callback(self, instance:INSTANCE) -> None:
        instance_id = id(instance)
        if (callbacks := self.callbacks.get(instance_id, False)):
            for i, cback in enumerate(callbacks):
                method = cback()
                # need to unpack it as the callback is a weakref.WeakMethod
                # as such if the object that the method is linked to gets deleted (garbage collected)
                # the WeakMethod returns None rather than a callable method 
                if method:
                    method(self.tags)
                else:
                    self._remove_callback(instance_id, i)

    def _remove_callback(self, instance_id:int, index:int) -> None:
        cbacks:list = self.callbacks.get(instance_id)
        cbacks.pop(index)
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

def _make_container_mixin(_base_getter_cls:Union[CallbackNoGetterMixin, CallbackGetterMixin]) -> type:
    """
    Create a mixin for descriptors that wrap a container type (list or dict)

    takes _base_getter_cls which defines whether the descriptor has a getter method or not
    """
    class ContainerMixin(_base_getter_cls):

        _observable_types:dict = {
            type(list()): ObservableList,
            type(dict()): ObservableDict,
        }
        _is_wrapped:set = set()

        def __init__(self, *, fval:Callable[[INSTANCE, CBACK, Any], VAL] = _do_nothing, **kwargs):
            self.fval:Callable[[INSTANCE, CBACK, Any], VAL] = fval
            super().__init__(**kwargs)

        def _wrap_container_field(self, instance:INSTANCE) -> None:
            if (id(instance), id(self)) in self._is_wrapped:
                return
            
            val = getattr(instance, self.name)
            if type(val) not in self._observable_types:
                return
            
            cBack = partial(self._trigger_callback, weakref.ref(instance))
            ObservableType = self._observable_types.get(type(val))
            wrapped = ObservableType(val, callback=cBack)
            setattr(instance, self.name, wrapped)
            self._is_wrapped.add((id(instance), id(self)))

        def __get__(self, instance:INSTANCE, owner:OWNER) -> VAL:
            if instance is None:
                return self
            self._wrap_container_field(instance)
            return _base_getter_cls.__get__(self, instance, owner)

        def __set__(self, instance:INSTANCE, value:VAL) -> None:
            """
            no repeated check when setting attributes
            assume types are static, i.e. no changing attribute from int to a list or dict
            """
            setattr(instance, self.name, value)
            self._wrap_container_field(instance)
            self._trigger_callback(instance)

    return ContainerMixin

class PlainMixin():
    """
    mixin for descriptors who's value is a plain value, i.e. str, or int, or float.
    """
    def __set__(self, instance:INSTANCE, value:VAL) -> None:
        """
        no repeated check when setting attributes
        assume types are static, i.e. no changing attribute from int to a list or dict
        """
        setattr(instance, self.name, value)
        self._trigger_callback(instance)

class PlainValMixin():
    """
    mixin for descriptors who's value is a plain value, i.e. str, or int, or float, and includes a validator
    """
    def __init__(self, *, fval:Callable[[INSTANCE, CBACK, Any], VAL] = _do_nothing, **kwargs):
        self.fval:Callable[[INSTANCE, CBACK, Any], VAL]= fval
        super().__init__(**kwargs)

    def __set__(self, instance:INSTANCE, value:Any) -> None:
        """
        no repeated check when setting attributes
        assume types are static, i.e. no changing attribute from int to a list or dict
        """
        value = self.fval(instance, self, value)
        setattr(instance, self.name, value)
        self._trigger_callback(instance)

_callback_types = {}

def _dynamic_callback_type(container:bool=False, single:bool=False, getter:bool=False, validator:bool=False) -> type[DescriptorProtocol[VAL]]: 
    assert isinstance(container, bool), f"container must be a boolean, got {type(container)}"
    assert isinstance(single, bool), f"single must be a boolean, got {type(single)}"

    key = (container, single, getter)
    if key in _callback_types:
        return _callback_types[key]

    else:
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
            bases.append(_make_container_mixin(getter_cls))
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

def callback(type_hint:type[VAL], *, 
            container:bool=False, 
            single:bool=False, 
            **kwargs) -> DescriptorProtocol[VAL]:
    """
    fget: Callable[[Any, Any, Any], T] = None,
    fval:Union[Callable, None]=None,
    tags:Union[str,list]=None
    """
    if kwargs.get("fget", False):
        getter=True
    else: 
        getter=False

    if kwargs.get("fval", False):
        validator=True
    else: 
        validator=False

    cback_obj = _dynamic_callback_type(container=container, single=single, getter=getter,validator=validator)

    return cback_obj[type_hint](**kwargs)