import weakref

from attrs import define, field, fields
from typing import Any, ClassVar, Callable
from functools import partial

@define(slots=True)
class CallbackField():
    """
    Allows for properties to call on functions when changed. Used to hook onto selectors 
    which change allowed behaviour of certain files (Allowed metadata, columns, etc...)
    """

    name:str = field(init=False)
    _callbacks:dict[str, list] = field(factory=dict, alias="_callbacks")
    _finalizers:dict[str, Any] = field(factory=dict, alias="_finalizers")

    def __set_name__(self, owner, name):
        self.name = f"_{name}"

    def __attrs_post_init__(self):
        pass

    def __get__(self, instance, owner):
        """
        can add the following:
         
        if instance is None:
            return self
        
        Useful when the you need the callbackField obj to add_callbacks to
        at the moment the following works:

        Class.__getattribute__(Class, "number")
        """
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        """
        no repeated check when setting attributes
        assume types are static, i.e. no changing attribute from int to a list or dict
        """
        setattr(instance, self.name, value)
        instance_id = id(instance)
        callbacks = self._callbacks.get(instance_id, False)
        if callbacks:
            self._trigger_callback(instance_id)

    def _trigger_callback(self, id_instance:str):
        for i, cback in enumerate(self._callbacks.get(id_instance)):
            method = cback()
            if method:
                method()
            else:
                print("hello, first time removing")
                self._remove_callback(id_instance, i)

    def _remove_callback(self,id_instance:str, index:int):
        cbacks:list = self._callbacks.get(id_instance)
        cbacks.pop(index)
        if not cbacks:
            self._callbacks.pop(id_instance)

    def _remove(self, instance_id:str):
        self._callbacks.pop(instance_id)
        self._finalizers.pop(instance_id)

    def add_callback(self, instance:object, callback:Callable):
        """
        Adds a callback (a class method) for this attribute of the given instance
        The callback will trigger when setting the attribute to a new value, appending or changing keys for lists and dictionaries as well

        This method will only work for class methods, if it is a regular function then it is not supported (can be done but need to use weakref.ref() instead)
        """
        weak_callback = weakref.WeakMethod(callback)
        instance_id = id(instance)
        self._callbacks.setdefault(instance_id, []).append(weak_callback)
        _del_callback = partial(self._remove, instance_id)
        self._finalizers[instance_id] = weakref.finalize(instance, _del_callback)

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

@define(slots=True)
class schemaCallbackField(CallbackField):
    tag:str = field(init=True, kw_only=True)

    def __set__(self, instance, value):
        setattr(instance, self.name, value)
        callbacks = self._callbacks.get(id(instance), False)
        if callbacks:
            for cback in callbacks:
                cback(self.tag)

def wrap_callback_fields(instance:object):
    cls = instance.__class__
    for field in fields(cls):
        """
        check here and assign to callbackField
        """
        if field.name.startswith("_"):
            descriptor_name = field.name[1:]  # Try to find corresponding descriptor
            descriptor:CallbackField = cls.__dict__.get(descriptor_name, None) #(cls, descriptor_name)
            if not isinstance(descriptor_name, CallbackField):
                continue
          
        val = getattr(instance, field)
        cBack = partial(descriptor._trigger_callback(id(instance)))
        if isinstance(val, list):
            wrapped = ObservableList(val, callback=cBack)
            setattr(instance, field, wrapped)
        elif isinstance(val, dict):
            wrapped = ObservableDict(val, callback=cBack)
            setattr(instance, field, wrapped)