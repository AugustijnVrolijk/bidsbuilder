from collections.abc import MutableMapping, MutableSequence

class ObservableValidatorDict(MutableMapping):
    def __init__(self, data:dict):
        self._mapping = {}
        self.update(data)

    def __getitem__(self, key):
        return self._mapping[key]

    def __setitem__(self, key, value):
        print(f"hello: {key}")
        self._mapping[key] = value

    def __delitem__(self, key):
        del self._mapping[key]

    def __iter__(self):
        return iter(self._mapping)
    
    def __len__(self):
        return len(self._mapping)


class ObservableValidatorDict(MutableSequence):
    def __init__(self, data:dict):
        self._mapping = []
        self.extend()

    def __getitem__(self, key):
        return self._mapping[key]

    def __setitem__(self, key, value):
        print(f"hello: {key}")
        self._mapping[key] = value

    def __delitem__(self, key):
        del self._mapping[key]

    def __iter__(self):
        return iter(self._mapping)
    
    def __len__(self):
        return len(self._mapping)



t = {"a":1,
     "b":2,
     "c":3}

t2 = {"c":3,
     "d":4,
     "e":5}

h = ObservableValidatorDict(t)

h.update(t2)
h["f"] = 6