from bidsbuilder.schema.callback_property import CallbackField
from attrs import define, field
from typing import ClassVar

@define(slots=True)
class demo_property():
    number:ClassVar = CallbackField()

    _number:int = field(alias="_number")

def callback1():
    print("hello")

def callback2():
    print("ihhii")

print("1")
t1 = demo_property(10)
#t1.number = CallbackField(t1.number)

print("2")

demo_property.__getattribute__(demo_property, "number").add_callback(t1, callback1)
print(t1.number)
t1.number = 5
print(t1.number)
t1.number = 1
print(t1.number)

print("3")


"""
going to use DESCRIPTORS.

Need to double check usage with __slots__

also ensure I use weakref.weakrefdictionary if I keep a copy of the instance as a key. Otherwise I need to use id(instance)


REQUIREMENTS, THINK ABOUT SUPPORT FOR A LIST (.append)


NEED TO TEST THE FOLLOWING:
    IF I CAN CALLBACK AN INSTANCE SPECIFIC METHOD,

    I.e. IF I can store the _check_schema of the correct instance as the callback method.. Or if I need to store datasetCore._check_schema(instance)

"""