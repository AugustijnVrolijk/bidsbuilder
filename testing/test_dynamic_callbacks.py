from bidsbuilder.util.hooks import *
from typing import Union, ClassVar
from attrs import define, field

def sayHi(*args, **kwargs):
    print("Hello from the callback!")

@define(slots=True)
class tester():
    _test:list = field(factory=list, alias="_test")
    test:ClassVar = HookedDescriptor(list, callback=sayHi)
    _test2:str = field(default="whoop", alias="_test2")
    test2:ClassVar = HookedDescriptor(str, callback=sayHi, tags="test2w")

test1 = tester()
test1.test.append("Hello")
print("test appended")

test1.test2 = "value1"
print("test2 assigned")

print(test1.test)
print(type(tester.test))
print(getattr(tester.test2, 'tags', None))
test2 = {}
test2["key1"] = "hello"
