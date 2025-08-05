import weakref

from attrs import define, field, fields
from typing import Any, Callable, Generic, TypeVar, Union
from functools import partial

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

"""
def wrap_callback_fields(instance:object):
    cls = instance.__class__
    for field in fields(cls):
        
        # check here and assign to CallbackBase
        
        name:str = field.name
        if name.startswith("_"):
            descriptor_name = name[1:] 
            descriptor:CallbackBase = getattr(cls, descriptor_name, None) #cls.__dict__.get(descriptor_name, None) 
            if not isinstance(descriptor, CallbackBase):
                continue
          
        val = getattr(instance, name)
        cBack = partial(descriptor._trigger_callback, weakref.ref(instance))
        if isinstance(val, list):
            wrapped = ObservableList(val, callback=cBack)
            setattr(instance, name, wrapped)
        elif isinstance(val, dict):
            wrapped = ObservableDict(val, callback=cBack)
            setattr(instance, name, wrapped)
"""
