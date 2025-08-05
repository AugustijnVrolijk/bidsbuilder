from bidsbuilder.util.reactive import CallbackField, wrap_callback_fields
from attrs import define, field
from typing import ClassVar

from unittest.mock import Mock

@define(slots=True)
class demo_property():
    number:ClassVar = CallbackField[int]()
    #number:ClassVar = schemaCallbackField(tag="number")

    _number:int = field(alias="_number")

    def __attrs_post_init__(self):
        wrap_callback_fields(self)

@define(slots=True)
class demo_property_getter():
    myStr:ClassVar[str]
    #number:ClassVar = schemaCallbackField(tag="number")

    _myStr:str = field(alias="_myStr")

    """interestingly as the descriptor passes the instance as the first variable, it could be written
    either as a static method or instance method as in _number_getter. Ill keep it as static to make it 
    clear they are descriptor getters"""
    @staticmethod
    def _static_number_getter(instance, descriptor, owner):
        return instance._myStr + descriptor.tags

    myStr:ClassVar[str] = CallbackField[str](fget=_static_number_getter, tags=" woohoo")

    def _number_getter(self, descriptor, owner):
        
        return self._myStr + descriptor.tags

    myStr:ClassVar[str] = CallbackField[str](fget=_number_getter, tags=" woohoo")

    def __attrs_post_init__(self):
        wrap_callback_fields(self)

@define(slots= True)
class demo_list_validator_property():
    myItems:ClassVar[list]

    _myItems:list = field(factory=list,alias="_myItems")

    def __attrs_post_init__(self):
        wrap_callback_fields(self)

    @staticmethod
    def _validate_myItems(instance, descriptor, value):
        value += 5
        return value

    myItems:ClassVar = CallbackField[list](fval=_validate_myItems)

@define(slots=True)
class demo_smthElse():

    _value1 = field()
    _mock_input:Mock = field()

    
    def my_callback(self, *args, **kwargs):
        to_input = self._value1 + 5
        self._mock_input(to_input)


def test_basic_instance_callbacks():
    t1 = demo_property(10)
    t2 = demo_property(10000)
    _mock1 = Mock()
    _mock2 = Mock()
    smth1 = demo_smthElse(5, _mock1)
    smth2 = demo_smthElse(1343, _mock2)

    assert t2.number == 10000 and t1.number == 10

    t1.number = 5
    _mock1.assert_not_called()
    _mock2.assert_not_called()
    assert t2.number == 10000 and t1.number == 5

    getattr(demo_property, "number").add_callback(t1, smth1.my_callback)
    t1.number = 1
    t2.number = 58193
    _mock1.assert_called_once_with(10)
    _mock2.assert_not_called()
    assert t2.number == 58193 and t1.number == 1

    getattr(demo_property, "number").add_callback(t2, smth2.my_callback)
    t2.number = 1345875357
    _mock1.assert_called_once_with(10)
    _mock2.assert_called_once_with(1348)
    assert t2.number == 1345875357 and t1.number == 1

def test_self_cleaning_callbacks():
    cur_callbacks = getattr(demo_property, "number").callbacks
    print(f"Beginning before creation \n{cur_callbacks}\n")
    t1 = demo_property(10)
    t2 = demo_property(10000)
    smth1 = demo_smthElse(5)
    smth2 = demo_smthElse(1343)
    getattr(demo_property, "number").add_callback(t1, smth1.my_callback1)
    getattr(demo_property, "number").add_callback(t2, smth2.my_callback2)

    cur_callbacks = getattr(demo_property, "number").callbacks
    print(f"before t2 deletion \n{cur_callbacks}\n")
    del t2
    import gc
    gc.collect()
    after_callbacks = getattr(demo_property, "number").callbacks
    print(f"after deletion, weakref.finalizer should clean up descriptor reference \n{after_callbacks}") 

def test_deleted_callback():
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

def test_correct_callback_inputs():
    pass

def test_list_callback():
    t1 = demo_list_validator_property([10,4,2])
    
    _mock1 = Mock()
    smth1 = demo_smthElse(100, _mock1)

    getattr(demo_list_validator_property, "myItems").add_callback(t1, smth1.my_callback)

    t1.myItems = [1, 2, 3, 4, 5]
    _mock1.assert_called_once_with(105)
    assert t1.myItems == [1, 2, 3, 4, 5]

    t1.myItems.append(4)
    _mock1.assert_has_calls([105, 105])
    assert t1.myItems == [10,4,2,4]
    
def test_custom_getter_callback():
    t1 = demo_property_getter("yes")
    print(f"first print: {t1.myStr}")
    t1.myStr = "no"
    print(f"second print print: {t1.myStr}")

def test_validator():
    ...

if __name__ == "__main__":
    test_basic_instance_callbacks()
    test_list_callback()
    test_deleted_callback()
    test_self_cleaning_callbacks()
    test_custom_getter_callback()
    test_validator()