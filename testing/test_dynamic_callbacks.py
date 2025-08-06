from bidsbuilder.util.reactive import *
from typing import Union, ClassVar
from attrs import define, field

def sayHi(*args, **kwargs):
    print("Hello from the callback!")


@define(slots=True)
class tester():
    _test:list = field(factory=list, alias="_test")
    test:ClassVar = callback(list,container=True, single=True, callback=sayHi)
    _test2:dict = field(factory=dict, alias="_test2")
    test2:ClassVar = callback(dict,container=True, single=True, callback=sayHi, tags="test2w")


test1 = tester()
test1.test.append("Hello")
test1.test2["key1"] = "value1"
print(test1.test)
print(type(tester.test))
print(getattr(tester.test2, 'tags', None))
test2 = {}
test2["key1"] = "hello"
