
from typing import Callable

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