from bidsbuilder.util.reactive import *
from typing import Union, ClassVar

def sayHi(*args, **kwargs):
    print("Hello from the callback!")

class tester():
    test:ClassVar = callback(container=True, single=True, callback=sayHi)
    
    def __init__(self):
        _test:Union[int, None] = 1


test = tester()
test.test = 5

print(type(tester.test))