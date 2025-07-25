from attrs import define, field
from typing import Any

@define(slots=True)
class CallbackField:
    """
    Allows for properties to call on functions when changed. Used to hook onto selectors 
    which change allowed behaviour of certain files (Allowed metadata, columns, etc...)
    """
    val:Any = field(repr=True)
    _callbacks:dict = field(factory=dict, alias="_callbacks")
    _values:dict = field(factory=dict, alias="_values")

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