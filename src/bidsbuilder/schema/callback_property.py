import weakref

from attrs import define, field, fields
from typing import Any, Callable, Generic, TypeVar
from functools import partial

def _do_nothing(*args, **kwargs) -> True:
    return True

T = TypeVar("T")

@define(slots=True)
class CallbackBase(Generic[T]):
    """
    base descriptor class for callbacks
    """

    name:str = field(init=False)

    def __set_name__(self, owner, name):
        """add underscore for instance variable. All classes are slotted so cannot use
        __dict__. Consequently use '_' to denote the raw attribute and store it on the instance
        also makes debugging easier as the instance owns its attributes"""
        self.name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        setattr(instance, self.name, value)
        self._trigger_callback(instance)

    def _trigger_callback(self):
        ...

@define(slots=True)
class CallbackField(CallbackBase, Generic[T]):
    """
    Allows for properties to call on functions when changed. Used to hook onto selectors 
    which change allowed behaviour of certain files (Allowed metadata, columns, etc...)
    """

    validator: Callable = field(default=_do_nothing, alias="_validator")
    callbacks:dict[str, list] = field(factory=dict, alias="_callbacks")
    finalizers:dict[str, Any] = field(factory=dict, alias="_finalizers")

    def __set__(self, instance, value):
        """
        no repeated check when setting attributes
        assume types are static, i.e. no changing attribute from int to a list or dict
        """
        if not self.validator(instance, value):
            return
        
        setattr(instance, self.name, value)
        self._trigger_callback(instance)

    def _trigger_callback(self, instance:object):
        instance_id = id(instance)
        callbacks = self.callbacks.get(instance_id, False)
        if callbacks:
            for i, cback in enumerate(callbacks):
                method = cback()
                if method:
                    method()
                else:
                    self._remove_callback(instance_id, i)

    def _remove_callback(self,instance_id:str, index:int):
        cbacks:list = self.callbacks.get(instance_id)
        cbacks.pop(index)
        if not cbacks:
            self._remove(instance_id)

    def _remove(self, instance_id:str):
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

@define(slots=True)
class singleCallbackField(CallbackBase, Generic[T]):
    """
    Allows for properties to call on functions when changed. Used to hook onto selectors 
    which change allowed behaviour of certain files (Allowed metadata, columns, etc...)
    """

    #_validator: Callable = field(default=_do_nothing, alias="_validator")
    callback: Callable = field()

    def _trigger_callback(self, instance):
        self.callback(instance)

class ObservableList(list):
    def __init__(self, data:list, callback: Callable):
        super().__init__(data)
        self._callback = callback
        self._frozen = False

    def _check_callback(self):
        if not self._frozen:
            self._callback()

    def append(self, item):
        super().append(item)
        self._check_callback()

    def extend(self, iterable):
        self._frozen = True
        super().extend(iterable)
        self._frozen = False
        self._check_callback()

    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self._check_callback()

    def __delitem__(self, index):
        super().__delitem__(index)
        self._check_callback()

    # Add more list methods as needed...

class ObservableDict(dict):
    def __init__(self, data:dict, callback:Callable):
        super().__init__(data)
        self._callback = callback
        self._frozen = False

    def _check_callback(self):
        if not self._frozen:
            self._callback()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._check_callback()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._check_callback()

    def update(self, *args, **kwargs):
        self.frozen = True
        super().update(*args, **kwargs)
        self.frozen = False
        self._check_callback()

def wrap_callback_fields(instance:object):
    cls = instance.__class__
    for field in fields(cls):
        """
        check here and assign to callbackField
        """
        name:str = field.name
        if name.startswith("_"):
            descriptor_name = name[1:] 
            descriptor:CallbackField = getattr(cls, descriptor_name, None) #cls.__dict__.get(descriptor_name, None) 
            if not isinstance(descriptor, CallbackField):
                continue
          
        val = getattr(instance, name)
        cBack = partial(descriptor._trigger_callback, weakref.ref(instance))
        if isinstance(val, list):
            wrapped = ObservableList(val, callback=cBack)
            setattr(instance, name, wrapped)
        elif isinstance(val, dict):
            wrapped = ObservableDict(val, callback=cBack)
            setattr(instance, name, wrapped)