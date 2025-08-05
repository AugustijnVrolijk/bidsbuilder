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
    """
    Mixin for descriptors that have a custom getter method which is given as a parameter

    i.e. for Suffix, Entity, or Datatype, where the custom getter can search parent instances
    if the current instance does not have the value set
    """
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
    """
    Mixin for descriptors that do not have a getter method, i.e. they use the default getter
    """
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
    Mixin for per-instance callbacks, i.e. each instance of the descriptor can have its own callback/callbacks

    Useful for attributes such as exists, enabling callback checking for other objects which depend on their 
    exists value. I.e. dataset_description is dependent on genetic_info existing.
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
    Mixin for single callbacks, i.e. only one callback can be registered for this field 
    and is applied to all instances of the descriptor

    at the time of writing, this is used for the callbacks of "parent" attributes.
    i.e. Entity, Suffix, or datatype, where the single callback is defined to make each "child"
    and the parent itself check their schema / update their tree name reference
    """
    def __init__(self, *, callback:Callable, **kwargs):
        self.callback:Callable = callback
        super().__init__(**kwargs)

    def _trigger_callback(self, instance):
        self.callback(instance)

def _make_container_mixin(_base_getter_cls):
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

        def __init__(self, *, fval: Callable[[T], T] = _do_nothing, **kwargs):
            self.fval: Callable[[T], T] = fval
            super().__init__(**kwargs)

        def _wrap_container_field(self, instance:object):
            if id(instance) in self._is_wrapped:
                return
            
            val = getattr(instance, self.name)
            if type(val) not in self._observable_types:
                return
            
            cBack = partial(self._trigger_callback, weakref.ref(instance))
            ObservableType = self._observable_types[type(val)]
            wrapped = ObservableType(val, callback=cBack)
            setattr(instance, self.name, wrapped)
            self._is_wrapped.add(id(instance))

        def __get__(self, instance, owner):
            if instance is None:
                return self
            self._wrap_container_field(instance)
            return _base_getter_cls.__get__(self, instance, owner)

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
    """
    mixin for descriptors who's value is a plain value, i.e. str, or int, or float.
    """
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

class callbackFactory():

    @staticmethod
    def _dynamic_callback_type(container:bool=False, single:bool=False, getter:bool=False):
        assert isinstance(container, bool), f"container must be a boolean, got {type(container)}"
        assert isinstance(single, bool), f"single must be a boolean, got {type(single)}"
        assert isinstance(getter, bool), f"getter must be a boolean, got {type(getter)}"

        key = (container, single, getter)
        if key in _callback_types:
            return _callback_types[key]

        else:
            bases = [Generic[T]]
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
            # it gives me an error if I try pass them as kwds={}...
            # so I just define it after...
            ret_callback_type = types.new_class(name, tuple(bases),kwds={})
            ret_callback_type.__module__ = __name__
            _callback_types[key] = ret_callback_type
            return ret_callback_type

    @staticmethod
    def _make_callback_instance(type_hint:TypeVar, 
                                container:bool=False, 
                                single:bool=False, 
                                **kwargs) -> Generic[T]:
        """
        fget: Callable[[Any, Any, Any], T] = None,
        fval:Union[Callable, None]=None,
        tags:Union[str,list]=None
        """
        if kwargs.get("fget", False):
            getter=True
        else: 
            getter=False
            
        cback_obj = callback._dynamic_callback_type(container=container, single=single, getter=getter)

        return cback_obj[type_hint](**kwargs)

    def __class_getitem__(cls, type_hint) -> Generic[T]:
        def constructor(**kwargs):
            return cls._make_callback_instance(type_hint=type_hint, **kwargs)
        
        return constructor
    
callback = callbackFactory
