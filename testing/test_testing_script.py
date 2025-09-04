from bidsbuilder.util.hooks.containers import *
import inspect
import types
from bidsbuilder.util.hooks.new_containers import MinimalList

class toMerge():

    def post__init__(self, x2):
        self.x2 = x2

    def addSelf(self):
        sum = self.x1 + self.y1 + self.x2
        print(sum)
        return sum

class test1():

    def __init__(self, x1, y1):
        self.x1 = x1
        self.y1 = y1

def merge(base_container:object):
    cur_type = base_container.__class__
    name = "tester2"
    dynamic_container = types.new_class(name, (cur_type, toMerge),kwds={})
    base_container.__class__ = dynamic_container
    return base_container

def make_proxying_init_for(base_init):
    sig = inspect.signature(base_init)
    def __init__(self, *args, **kwargs):
        bound = sig.bind(self, *args, **kwargs)
        base_init(*bound.args, **bound.kwargs)
        # no observable init here; we’ll inject post-init anyway
    return __init__

def make_dynamic(base, observable):
    def __init__(self, *args, **kwargs):
        # figure out what init belongs to the base
        base_init = base.__init__
        sig = inspect.signature(base_init)

        # bind args/kwargs to the base signature
        bound = sig.bind(self, *args, **kwargs)
        base_init(*bound.args, **bound.kwargs)

        # then inject observable state
        observable.__init__(self, descriptor=kwargs.get("descriptor"), weakref=kwargs.get("weakref"))

    return type(f"Observable{base.__name__}", (base, observable), {"__init__": __init__})


class tester_list():
    def _check_callback(self):
        print("do nothings")

def create_tester_list(*args, **kwargs) -> object:
    dynamic_container = types.new_class("tester_list_1", (tester_list, MinimalList),kwds={})
    ret_instance = dynamic_container(*args, **kwargs)
    return ret_instance

if __name__ == "__main__":
    """
    t1 = test1(5,6)
    t2 = merge(t1)
    t2.post__init__(8)
    final = t2.addSelf()
    print(final)
    """
    t1 = MinimalList([1,2,3,4,5])
    print(t1.__repr__())
    t2 = create_tester_list([1,4])
    print(t2.__repr__())
    t2._check_callback()
    print(issubclass(t2.__class__, MinimalList))
    print(issubclass(t1.__class__, MinimalList))  