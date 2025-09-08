from bidsbuilder.util.hooks.containers import *
import types
from bidsbuilder.util.hooks.new_containers import *
from functools import wraps

from collections.abc import MutableMapping, MutableSequence, MutableSet
from typing import Union


def method1(self, a):
    print(a)
    return

class test1():
    __slots__ = ["var1", "var2"]
    def method2(self, a):
        print(f"hi {a}")
        return


def inherit_class(to_inherit):
    class to_inherit(test1):
        ...

    
    return to_inherit

def testerino(**kwargs):
    print(kwargs)
    return

def main():
    t1 = types.new_class("MyNewClass", (), kwds={}, exec_body=lambda ns: ns.update({"method1": method1, "__slots__":["var3", "var4"]}))
 
    tester = t1()
    tester.method1("there")
    #tester.method2("there")
    test2 = inherit_class(t1)

    tester.var3 = 10
    tester.var4 = 20

    #print(tester.__dict__)


    tester2 = test2()
    tester2.var1 = 5
    tester2.var2 = 10
    tester2.var3 = 15
    tester2.var4 = 20

    print(tester2.__dict__)

    tester3 = test1()
    tester3.var3 = 15
    tester3.var4 = 20
    print(tester3.__dict__)

if __name__ == "__main__":
    main()



  
class MinimalDict(MutableMapping):
    def __init__(self, *args, **kwargs): self._data:dict = dict(*args, **kwargs)
    def __getitem__(self, key): return self._data[key]
    def __setitem__(self, key, value): self._data[key] = value
    def __delitem__(self, key): del self._data[key]
    def __iter__(self): return iter(self._data)
    def __len__(self): return len(self._data)

class MinimalList(MutableSequence):
    def __init__(self, *args, **kwargs): self._data:list = list(*args, **kwargs)
    def __getitem__(self, index): return self._data[index]
    def __setitem__(self, index, value): self._data[index] = value
    def __delitem__(self, index): del self._data[index]
    def __len__(self):  return len(self._data)
    def insert(self, index, value): self._data.insert(index, value)

class MinimalSet(MutableSet):
    def __init__(self, *args, **kwargs): self._data:set = set(*args, **kwargs)
    def __contains__(self, value): return value in self._data
    def __iter__(self): return iter(self._data)
    def __len__(self): return len(self._data)
    def add(self, value): self._data.add(value)
    def discard(self, value): self._data.discard(value)

class ObservableType():
    def __observable_container_init__(self, descriptor, weakref):
        names = ("_descriptor_", "_object_ref_", "_frozen_flag_")
        for n in names:
            if getattr(self, n, False):
                raise TypeError(f"Observable objects reserve the attribute name: {n}\n Please rename this attribute to something else")

        setattr(self, names[0], descriptor)
        setattr(self, names[1], weakref)
        setattr(self, names[2], False)

    def __check_callback__(self):
        if not self._frozen_flag_:
            self._descriptor_._trigger_callback(self._object_ref_()) # weak reference so need to call it to access it

class obs_container_factory():
    """
    Factory class to create observable container types on the fly.

    checks the methods in the given base container and creates an observable wrapper around them.

    set type class attributes, i.e. module scope as this file etc..
    """
    @staticmethod
    def _get_name(base_container:type, validator_flag:bool) -> str:
        return f"Observable{'Validator' if validator_flag else ''}{base_container.__name__}"

    @classmethod
    def create(cls, base_container:type, validator_flag:bool) -> ObservableType:
        namespace = {}

        for (orig_method, func_name)  in cls.iter_methods_set(cls.check_callback_methods):
            namespace[func_name] = cls.wrap_check_callback(orig_method)

        for (orig_method, func_name)  in cls.iter_methods_set(cls.frozen_check_callback_methods):
            namespace[func_name] = cls.wrap_frozen_check_callback(orig_method)

        dynamic_container = types.new_class(cls._get_name(base_container, validator_flag), (ObservableType),kwds={}, exec_body=lambda ns: ns.update(namespace))

        if validator_flag:
            cls.wrap_with_validator()
        
        return dynamic_container

    def wrap_with_validator(self):
        for (orig_method, func_name)  in self.iter_methods_set(self.validate_input_methods):
            setattr(self.dynamic_container, func_name, self.wrap_validate_input(orig_method))

        _validator_init_name_ = "__observable_container_init__"
        _validator_init_ = getattr(self.dynamic_container, _validator_init_name_)
        setattr(self.dynamic_container, _validator_init_name_, self.wrap_validate_instance_creation(_validator_init_))

    def iter_methods_set(self, to_iter):
        for func_name in to_iter:
            if orig_method := getattr(self.dynamic_container, func_name, False):
                yield (orig_method, func_name)

    check_callback_methods = ("__setitem__", "__delitem__", "insert", "add", "discard")
    frozen_check_callback_methods = ("update", "extend")
    validate_input_methods = ("__setitem__", "insert", "add")

    @staticmethod
    def wrap_check_callback(orig_method):
        @wraps(orig_method)
        def _wrapped(self:ObservableType, *args, **kwargs):
            orig_method(self, *args, **kwargs)
            self.__check_callback__()
        return _wrapped

    @staticmethod
    def wrap_frozen_check_callback(orig_method):
        @wraps(orig_method)
        def _wrapped(self:ObservableType, *args, **kwargs):
            self._frozen_flag_ = True
            orig_method(self, *args, **kwargs)
            self._frozen_flag_ = False
            self.__check_callback__()
        return _wrapped

    @staticmethod
    def wrap_validate_input(orig_method):  
        @wraps(orig_method)
        def _wrapped(self:ObservableType, *args, **kwargs):
            n_args = self._descriptor_.fval(self._object_ref_(), self._descriptor_, *args, **kwargs)
            orig_method(self, *n_args, **kwargs)
        return _wrapped
    
    @staticmethod
    def wrap_validate_instance_creation(orig_method):

        @wraps(orig_method)
        def _wrapped(self:ObservableType, *args, **kwargs):
            orig_method(self, *args, **kwargs)
            
            self._frozen_flag_ = True

            if isinstance(self, MinimalList):
                 for i in range(len(self)):
                    self[i] = self[i]
            elif isinstance(self, MinimalDict):
                vals = [k for k in self]
                for key in vals:
                    val = self.pop(key)
                    self[key] = val
            elif isinstance(self, MinimalSet):
                vals = [item for item in self]
                for val in vals:
                    self.remove(val)
                    self.add(val)
            else:
                raise NotImplementedError(f"Validator wrapping not implemented for {self.__class__}")
        
            self._frozen_flag_ = False

        return _wrapped