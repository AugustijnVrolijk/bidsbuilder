import weakref

import types

from attrs import define, field, fields
from typing import Any, Callable, Generic, TypeVar, Union
from functools import partial
from .containers import ObservableList, ObservableDict

def _do_nothing(instance: object, descriptor, value:Any, *args, **kwargs) -> Any:
    return value

def _def_get(instance, descriptor, owner):
    return 

T = TypeVar("T")

class CallbackGetterMixin():

    def __init__(self, *, fget:Callable[[Any, Any, Any], T], tags:Union[list, None]=None, **kwargs):
        self.fget:Callable[[Any, Any, Any], T] = fget
        self.tags:Union[list, None] = tags
        super().__init__(**kwargs)

    def __set_name__(self, owner, name):
        """add underscore for instance variable. All classes are slotted so cannot use
        __dict__. Consequently use '_' to denote the raw attribute and store it on the instance
        also makes debugging easier as the instance owns its attributes"""
        self.name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.fget(instance, self, owner)
    
class CallbackNoGetterMixin():

    def __init__(self, *, tags:Union[list, None]=None, **kwargs):
        self.tags:Union[list, None] = tags
        super().__init__(**kwargs)

    def __set_name__(self, owner, name):
        """add underscore for instance variable. All classes are slotted so cannot use
        __dict__. Consequently use '_' to denote the raw attribute and store it on the instance
        also makes debugging easier as the instance owns its attributes"""
        self.name:str = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name)

class PerInstanceCallbackMixin():
    """
    Allows for properties to call on functions when changed. Used to hook onto selectors 
    which change allowed behaviour of certain files (Allowed metadata, columns, etc...)
    """

    def __init__(self, **kwargs):
        self.callbacks:dict[str, list] = {}
        self.finalizers:dict[str, Any] = {}
        super().__init__(**kwargs)

    def _trigger_callback(self, instance:object):
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

    def _remove_callback(self,instance_id:int, index:int):
        cbacks:list = self.callbacks.get(instance_id)
        cbacks.pop(index)
        if not cbacks:
            self._remove(instance_id)

    def _remove(self, instance_id:int):
        self.callbacks.pop(instance_id)
        cur_finaliser:weakref.finalize = self.finalizers.pop(instance_id)
        cur_finaliser.detach()
        
    def add_callback(self, instance:object, callback:Callable):
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
    Allows for properties to call on functions when changed. Used to hook onto selectors 
    which change allowed behaviour of certain files (Allowed metadata, columns, etc...)
    """
    def __init__(self, *, callback:Callable, **kwargs):
        self.callback:Callable = callback
        super().__init__(**kwargs)

    def _trigger_callback(self, instance):
        self.callback(instance)

def _make_container_mixin(_base_getter_cls):

    class ContainerMixin(_base_getter_cls):

        _observable_types:dict = {
            type(list): ObservableList,
            type(dict): ObservableDict
        }

        def __init__(self, *, fval: Callable[[T], T] = _do_nothing, **kwargs):
            self.fval: Callable[[T], T] = fval
            super().__init__(**kwargs)

        def _wrap_container_field(self, instance:object):
            val = getattr(instance, self.name)
            if val not in self._observable_types.keys():
                return
            
            cBack = partial(self._trigger_callback, weakref.ref(instance))
            ObservableType = self._observable_types[type(val)]
            wrapped = ObservableType(val, callback=cBack)
            setattr(instance, self.name, wrapped)

        def __get__(self, instance, owner):
            if instance is None:
                return self
            self._wrap_container_field(instance)
            return super().__get__(instance, owner)

        def __set__(self, instance, value):
            """
            no repeated check when setting attributes
            assume types are static, i.e. no changing attribute from int to a list or dict
            """
            setattr(instance, self.name, value)
            self._wrap_container_field(instance)
            self._trigger_callback(instance)

    return ContainerMixin

class PlainValMixin():
    
    def __init__(self, *, fval: Callable[[T], T] = _do_nothing, **kwargs):
        self.fval: Callable[[T], T] = fval
        super().__init__(**kwargs)

    def __set__(self, instance, value):
        """
        no repeated check when setting attributes
        assume types are static, i.e. no changing attribute from int to a list or dict
        """
        value = self.fval(instance, self, value)
        setattr(instance, self.name, value)
        self._trigger_callback(instance)

_callback_types = {}

def callback(container:bool=False, 
             single:bool=False, 
             #fget:Union[Callable, None]=None, 
             **kwargs
             ) -> Generic[T]:
    
    """
    fval:Union[Callable, None]=None,
    tags:Union[str,list]=None
    """
    if kwargs.get("fget", False):
        getter=True
    else: 
        getter=False
        
    cback_obj = _dynamic_callback_type(container=container, single=single, getter=getter)

    return cback_obj(**kwargs)

def _dynamic_callback_type(container:bool=False, single:bool=False, getter:bool=False):
    assert isinstance(container, bool), f"container must be a boolean, got {type(container)}"
    assert isinstance(single, bool), f"single must be a boolean, got {type(single)}"
    assert isinstance(getter, bool), f"getter must be a boolean, got {type(getter)}"

    key = (container, single, getter)
    if key in _callback_types:
        return _callback_types[key]

    else:
        bases = []
        name = f"{'Single' if single else 'Multi'}Callback{'Container' if container else 'Field'}{'Getter' if getter else ''}"

        if single:
            bases.append(SingleCallbackMixin)
        else:
            bases.append(PerInstanceCallbackMixin)

        if getter:
            getter = CallbackGetterMixin
        else:
            getter = CallbackNoGetterMixin

        if container:
            bases.append(_make_container_mixin(getter))
        else:
            bases.append(PlainValMixin)
            bases.append(getter)
        # {"__module__": __name__}
        ret_callback_type = types.new_class(name, tuple(bases),{})
        ret_callback_type.__module__ = __name__
        _callback_types[key] = ret_callback_type
        return ret_callback_type
    
