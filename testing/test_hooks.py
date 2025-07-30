from bidsbuilder.schema.callback_property import CallbackField, wrap_callback_fields
from attrs import define, field
from typing import ClassVar

@define(slots=True)
class demo_property():
    number:ClassVar = CallbackField[int]()
    #number:ClassVar = schemaCallbackField(tag="number")

    _number:int = field(alias="_number")

    def __attrs_post_init__(self):
        wrap_callback_fields(self)

def _validate_myItems(instance, value):
    print("hello this is me right now")
    print(instance._myItems)

    return True

@define(slots= True)
class demo_list_property():
    myItems:ClassVar = CallbackField[list](_validator=_validate_myItems)

    _myItems:list = field(factory=list,alias="_myItems")

    def __attrs_post_init__(self):
        wrap_callback_fields(self)


@define(slots=True)
class demo_smthElse():

    _value1 = field()
    def __attrs_post_init__(self):
        wrap_callback_fields(self)

    def my_callback1(self):
        return print(self._value1 + 5)

    def my_callback2(self):
        return print(self._value1 / 5)




def check_basic_callbacks():
    t1 = demo_property(10)
    t2 = demo_property(10000)
    smth1 = demo_smthElse(5)
    smth2 = demo_smthElse(1343)
    print(f"first print: {t1.number}")
    t1.number = 5
    demo_property.__getattribute__(demo_property, "number").add_callback(t1, smth1.my_callback1)
    print(f"second print: {t1.number}")
    t1.number = 1
    print(f"third print: {t1.number}")

    print(f"t2 with smth2")
    print(f"first print: {t2.number}")
    t2.number = 58193
    demo_property.__getattribute__(demo_property, "number").add_callback(t2, smth2.my_callback2)
    print(f"second print: {t2.number}")
    t2.number = 1345875357
    print(f"third print: {t2.number}")

def check_self_cleaning_callbacks():
    cur_callbacks = getattr(demo_property, "number")._callbacks
    print(f"Beginning before creation \n{cur_callbacks}\n")
    t1 = demo_property(10)
    t2 = demo_property(10000)
    smth1 = demo_smthElse(5)
    smth2 = demo_smthElse(1343)
    getattr(demo_property, "number").add_callback(t1, smth1.my_callback1)
    getattr(demo_property, "number").add_callback(t2, smth2.my_callback2)

    cur_callbacks = getattr(demo_property, "number")._callbacks
    print(f"before t2 deletion \n{cur_callbacks}\n")
    del t2
    import gc
    gc.collect()
    after_callbacks = getattr(demo_property, "number")._callbacks
    print(f"after deletion, weakref.finalizer should clean up descriptor reference \n{after_callbacks}") 

def check_deleted_callback():
    t1 = demo_property(10)
    smth1 = demo_smthElse(5)
    getattr(demo_property, "number").add_callback(t1, smth1.my_callback1)
    print(f"first print/before assigning: {t1.number}")
    t1.number = 1
    print(f"after assigning")
    del smth1
    import gc
    gc.collect()
    print(f"after deleting callback reference")
    print(f"second print/before assigning: {t1.number}")
    t1.number = 58193
    print(f"after assigning")
    t1.number = 32523
    t1.number = 23

def check_list_callback():
    t1 = demo_list_property([10,4,2])

    smth1 = demo_smthElse(5)
    
    getattr(demo_list_property, "myItems").add_callback(t1, smth1.my_callback1)

    t1.myItems.append(4)
    print(t1.myItems)
    t1.myItems = [1, 2, 3, 4, 5]
    print(t1.myItems)

if __name__ == "__main__":
    

    print("BEFORE")
    myItems = [10, 4, 2]
    myItems.append(4)
    print(myItems)
    print("after")

    check_list_callback()
    print("hello")
    check_basic_callbacks()
    check_deleted_callback()
    check_self_cleaning_callbacks()


"""
going to use DESCRIPTORS.

Need to double check usage with __slots__

also ensure I use weakref.weakrefdictionary if I keep a copy of the instance as a key. Otherwise I need to use id(instance)


REQUIREMENTS, THINK ABOUT SUPPORT FOR A LIST (.append)


NEED TO TEST THE FOLLOWING:
    IF I CAN CALLBACK AN INSTANCE SPECIFIC METHOD,

    I.e. IF I can store the _check_schema of the correct instance as the callback method.. Or if I need to store datasetCore._check_schema(instance)

"""