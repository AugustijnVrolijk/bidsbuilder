import weakref

from attrs import define, field
from typing import Any, ClassVar
from functools import partial

@define(slots=True)
class OLDCallbackField:
    """
    Allows for properties to call on functions when changed. Used to hook onto selectors 
    which change allowed behaviour of certain files (Allowed metadata, columns, etc...)
    """
    val:Any = field(repr=True)
    _callbacks:dict = field(factory=dict, alias="_callbacks")
    _values:dict = field(factory=dict, alias="_values")

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._values.get(id(instance), self.val)

    def __set__(self, instance, value):
        old_value = self._values.get(id(instance), self.val)
        self._values[id(instance)] = value
        for cb in self._callbacks.get(id(instance), []):
            cb(instance, self.val, old_value, value)

    def add_callback(self, instance, callback):
        self._callbacks.setdefault(id(instance), []).append(callback)

    def __str__(self):
        return str(self.val)
    

@define(slots=True)
class CallbackField:
    """
    Allows for properties to call on functions when changed. Used to hook onto selectors 
    which change allowed behaviour of certain files (Allowed metadata, columns, etc...)
    """

    name:str = field(init=False)
    _callbacks:dict[str, list] = field(factory=dict, alias="_callbacks")
    _finalizers:dict[str, Any] = field(factory=dict, alias="_finalizers")

    def __set_name__(self, owner, name):
        self.name = f"_{name}"

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        print("hello")
        setattr(instance, self.name, value)
        callbacks = self._callbacks.get(id(instance), False)
        if callbacks:
            print("before here")
            for cback in callbacks:
                print("here")
                cback()

    def _remove(self, instance_id):
        self._callbacks.pop(instance_id)
        self._finalizers.pop(instance_id)

    def add_callback(self, instance, callback):
        instance_id = id(instance)
        self._callbacks.setdefault(instance_id, []).append(callback)
        _del_callback = partial(self._remove, instance_id)
        self._finalizers[instance_id] = weakref.finalize(instance, _del_callback)