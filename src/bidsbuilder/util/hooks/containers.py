
from typing import TYPE_CHECKING, Union
from weakref import ReferenceType

from collections.abc import MutableMapping, MutableSequence, MutableSet

if TYPE_CHECKING:
    from .descriptors import DescriptorProtocol

"""trying to avoid needing to re-implement every function. Ideally I only want to need to customise __setitem__ 
and __delitem__... but the assumption that .update calls on setitem in a loop is wrong, similarly .pop doesn't call
__delitem__... https://treyhunner.com/2019/04/why-you-shouldnt-inherit-from-list-and-dict-in-python/#:~:text=When%20inheriting%20from%20dict%20to,you%20might%20expect%20they%20would.

will use collections.abc mutable types in order to ensure all higher order methods are directed via the base methods.
"""

class ObservableType():
    def __init__(self, descriptor:'DescriptorProtocol', weakref:ReferenceType):
        super().__init__()
        self._data:Union[set,list,dict]
        self._descriptor:'DescriptorProtocol' = descriptor
        self._ref:ReferenceType = weakref 
        self._frozen:bool = False

    def _check_callback(self):
        if not self._frozen:
            self._descriptor._trigger_callback(self._ref()) # weak reference so need to call it to access it

    def __repr__(self):
        return repr(self._data)

    def __str__(self):
        return str(self._data)
    
    def __eq__(self, other):
        return self._data == getattr(other, '_data', other)

    def __ne__(self, other):
        return self._data != getattr(other, '_data', other)

    def __lt__(self, other):
        return self._data < getattr(other, '_data', other)

    def __le__(self, other):
        return self._data <= getattr(other, '_data', other)

    def __gt__(self, other):
        return self._data > getattr(other, '_data', other)

    def __ge__(self, other):
        return self._data >= getattr(other, '_data', other)

class ObservableList(MutableSequence, ObservableType):

    def __init__(self, data:list, descriptor:'DescriptorProtocol', weakref:ReferenceType):
        ObservableType.__init__(self, descriptor, weakref)
        self._data = []
        self.extend(data)

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value
        self._check_callback()

    def __delitem__(self, index):
        del self._data[index]
        self._check_callback()

    def __len__(self):
        return len(self._data)

    def insert(self, index, value):
        self._data.insert(index, value)
        self._check_callback()

    def extend(self, iterable):
        self._frozen = True
        super().extend(iterable)
        self._frozen = False
        self._check_callback()

class ObservableValidatorList(ObservableList):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        value = self._descriptor.fval(self._ref(), self._descriptor, value)
        super().__setitem__(key, value)

    def insert(self, index, value):
        value = self._descriptor.fval(self._ref(), self._descriptor, value)
        self._data.insert(index, value)

class ObservableDict(MutableMapping, ObservableType):

    def __init__(self, data:dict, descriptor:'DescriptorProtocol', weakref:ReferenceType):
        ObservableType.__init__(self, descriptor, weakref)
        self._data = {}
        self.update(data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._check_callback()

    def __delitem__(self, key):
        del self._data[key]
        self._check_callback()

    def __len__(self):
        return len(self._data)

    def update(self, *args, **kwargs):
        self.frozen = True
        super().update(*args, **kwargs)
        self.frozen = False
        self._check_callback()

    def __iter__(self):
        return iter(self._data)

class ObservableValidatorDict(ObservableDict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        value = self._descriptor.fval(self._ref(), self._descriptor, value)
        super().__setitem__(key, value)

class ObservableSet(MutableSet, ObservableType):

    def __init__(self, data:set, descriptor:'DescriptorProtocol', weakref:ReferenceType):
        ObservableType.__init__(self, descriptor, weakref)
        self._data = set()
        self.update()

    def __contains__(self, value):
        return value in self._data

    def __iter__(self):
        return iter(self._data)

    def add(self, value):
        self._data.add(value)
        self._check_callback()

    def discard(self, value):
        self._data.discard(value)
        self._check_callback()

    def __len__(self):
        return len(self._data)

    def update(self, data:set):
        self._frozen = True
        for v in data:
            self.add(v)
        self._frozen = False
        self._check_callback()

class ObservableValidatorSet(ObservableSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, value):
        value = self._descriptor.fval(self._ref(), self._descriptor, value)
        super().add(value)

__all__ = ["ObservableValidatorSet","ObservableSet","ObservableValidatorDict","ObservableDict","ObservableValidatorList","ObservableList", "ObservableType"]