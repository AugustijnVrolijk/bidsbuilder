from bidsbuilder.util.hooks import HookedDescriptor, DescriptorProtocol
from attrs import define, field
from typing import ClassVar
import gc

from unittest.mock import Mock, call

@define(slots=True)
class demo_property():
    number:ClassVar = HookedDescriptor(int)

    _number:int = field(alias="_number")

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

    myStr:ClassVar[str] = HookedDescriptor(str, fget=_static_number_getter, tags=" woohoo")

    def _number_getter(self, descriptor, owner):
        
        return self._myStr + descriptor.tags

@define(slots= True)
class demo_list_validator_property():
    myItems:ClassVar[list]
    _myItems:list = field(factory=list,alias="_myItems")

    @staticmethod
    def _validate_myItems(instance, descriptor, value):
        value += 5
        return value

    myItems:ClassVar[list] = HookedDescriptor(list, fval=_validate_myItems)

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

def test_deleted_instance():
    descriptor = demo_property.number
    assert len(descriptor.callbacks) == 0

    t1 = demo_property(10)
    t2 = demo_property(10000)
    mock1 = Mock()
    smth1 = demo_smthElse(17, mock1)
    smth2 = demo_smthElse(133, mock1)

    descriptor.add_callback(t1, smth1.my_callback)
    descriptor.add_callback(t2, smth2.my_callback)
    assert len(descriptor.callbacks) == 2
    assert id(t1) in descriptor.callbacks and id(t2) in descriptor.callbacks
   
    del t2
    gc.collect()
    assert id(t1) in descriptor.callbacks
    assert len(descriptor.callbacks) == 1

def test_deleted_callback():
    t1 = demo_property(10)
    _mock1 = Mock()
    smth1 = demo_smthElse(5, _mock1)
    smth2 = demo_smthElse(1343, _mock1)
    _mock1.assert_not_called()
    assert len(demo_property.number.callbacks) == 0
    demo_property.number.add_callback(t1, smth1.my_callback)
    demo_property.number.add_callback(t1, smth1.my_callback)
    demo_property.number.add_callback(t1, smth2.my_callback)
    assert id(t1) in demo_property.number.callbacks
    assert len(demo_property.number.callbacks[id(t1)]) == 3
    assert len(demo_property.number.callbacks.keys()) == 1
    t1.number = 1
    _mock1.assert_has_calls([call(10), call(10), call(1348)])
    del smth1
    gc.collect()
    t1.number = 58193
    """test after as the weak references stay until they are tried and removed if None"""
    assert len(demo_property.number.callbacks[id(t1)]) == 1 
    _mock1.assert_has_calls([call(10), call(10), call(1348), call(1348)])
    t2 = demo_property(5)
    demo_property.number.add_callback(t2, smth2.my_callback)
    assert len(demo_property.number.callbacks.keys()) == 2
    del smth2
    t1 = 5
    t2 = 5
    assert len(demo_property.number.callbacks) == 0
    _mock1.assert_has_calls([call(10), call(10), call(1348), call(1348)])

def test_list_callback():
    t1 = demo_list_validator_property([10,4,2])
    _mock1 = Mock()
    smth1 = demo_smthElse(100, _mock1)

    t1.myItems = [1, 2, 3, 4, 5]
    _mock1.assert_not_called()

    getattr(demo_list_validator_property, "myItems").add_callback(t1, smth1.my_callback)

    t1.myItems = [1, 2, 1, 4, 5]
    _mock1.assert_called_once_with(105)
    assert t1.myItems == [1, 2, 1, 4, 5]

    t1.myItems.append(4)
    _mock1.assert_has_calls([call(105), call(105)])
    assert t1.myItems == [1,2,1,4,5,4]
    
def test_custom_getter():
    instance = demo_property_getter("yes")
    descriptor = demo_property_getter.myStr

    # Check descriptor is using the right custom getter
    assert descriptor.fget is not None

    # Manually check that the descriptor getter uses the correct signature
    computed_value = instance.myStr  # triggers the descriptor's __get__
    assert computed_value == "yes woohoo" and instance._myStr == "yes"

    # Change underlying field
    instance._myStr = "no"
    assert instance.myStr == "no woohoo" and instance._myStr == "no"

    # Check that descriptor is called as a descriptor, not returning raw _myStr
    assert not isinstance(instance.__class__.myStr.__get__(None, instance.__class__), str)

def test_validator():
    ...

def test_correct_callback_inputs():
    ...

if __name__ == "__main__":
    print("Testing hooks 0")
    test_basic_instance_callbacks()
    print("Testing hooks 1")
    test_list_callback()
    print("Testing hooks 2")
    test_deleted_callback()
    print("Testing hooks 3")
    test_deleted_instance()
    print("Testing hooks 4")
    test_custom_getter()
    print("Testing hooks 5")

    # the following are not finished tests

    test_validator()
    test_correct_callback_inputs()