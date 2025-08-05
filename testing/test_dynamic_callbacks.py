from bidsbuilder.util.reactive import *
from typing import Union, ClassVar
from attrs import define, field

def sayHi(*args, **kwargs):
    print("Hello from the callback!")


@define(slots=True)
class tester():
    test:ClassVar = callback[list](container=True, single=True, callback=sayHi)
    
    test2:ClassVar = callback[list](container=True, single=True, callback=sayHi, tags="test2")

    _test:Union[list, None] = field(factory=list, alias="_test")
    _test2:Union[list, None] = field(factory=list, alias="_test2")

test1 = tester()
test1.test.append("Hello")
print(test1.test)
print(type(tester.test))

