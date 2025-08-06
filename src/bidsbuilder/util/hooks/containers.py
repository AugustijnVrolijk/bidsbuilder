
from typing import Any, TYPE_CHECKING
from weakref import ReferenceType

if TYPE_CHECKING:
    from .descriptors import DescriptorProtocol


class ObservableType():
    def __init__(self, descriptor:'DescriptorProtocol', weakref:ReferenceType):
        self._descriptor:'DescriptorProtocol' = descriptor
        self._ref:ReferenceType = weakref 
        self._frozen:bool = False

    def _check_callback(self):
        if not self._frozen:
            self._descriptor._trigger_callback(self._ref()) # weak reference so need to call it to access it

class ObservableList(list, ObservableType):

    def __init__(self, data:list, descriptor:'DescriptorProtocol', weakref:ReferenceType):
        list.__init__(self, data)
        ObservableType.__init__(self, descriptor, weakref)

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

class ObservableDict(ObservableType, dict):

    def __init__(self, data:dict, descriptor:'DescriptorProtocol', weakref:ReferenceType):
        dict.__init__(self, data)
        ObservableType.__init__(self, descriptor, weakref)

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