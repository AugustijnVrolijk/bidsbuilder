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

@define(slots=True)
class demo_list_property():

    _myItems:list = field(factory=list,alias="_myItems")
    myItems:ClassVar[list] = HookedDescriptor(list, tags="myItems")


@define(slots= True)
class demo_validator_property():
    myItems:ClassVar[dict]
    myName:ClassVar[str]


    @staticmethod
    def _validate_myItems(instance, descriptor, value):
        key, val = value
        val += 5
        return val
    
    _myItems:dict = field(factory=dict,alias="_myItems")
    myItems:ClassVar[dict] = HookedDescriptor(dict, fval=_validate_myItems)

    @staticmethod
    def _myName_getter(self, descriptor, Owner):
        to_add = descriptor.tags
        return f"{self._myName}{to_add}"

    @staticmethod
    def _validate_myName(self, descriptor, value):
        return f"Name: {value}"
    
    _myName:ClassVar[str] = field(default="nothing",alias="_myName")
    myName:ClassVar[str] = HookedDescriptor(str, fget=_myName_getter, fval=_validate_myName, tags=" hehe")


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
    t1 = demo_list_property([10,4,2])
    _mock1 = Mock()
    smth1 = demo_smthElse(100, _mock1)

    t1.myItems = [1, 2, 3, 4, 5]
    _mock1.assert_not_called()

    getattr(demo_list_property, "myItems").add_callback(t1, smth1.my_callback)

    t1.myItems = [1, 2, 1, 4, 5]
    _mock1.assert_called_once_with(105)
    assert t1.myItems == [1, 2, 1, 4, 5]
    assert [1,2,1,4,5] == t1.myItems

    assert t1.myItems != [1, 2, 3]
    assert [1, 2, 3] != t1.myItems

    assert [1, 2, 1, 4, 4] < t1.myItems    # 5 > 4 at last element
    assert t1.myItems < [1, 2, 1, 4, 6]    # 5 < 6 at last element

    # <=
    assert [1, 2, 1, 4, 5] <= t1.myItems
    assert t1.myItems <= [1, 2, 1, 4, 5]
    assert t1.myItems <= [1, 2, 1, 4, 6]

    # >
    assert [1, 2, 1, 4, 6] > t1.myItems
    assert t1.myItems > [1, 2, 1, 4, 4]

    # >=
    assert [1, 2, 1, 4, 5] >= t1.myItems
    assert t1.myItems >= [1, 2, 1, 4, 5]
    assert t1.myItems >= [1, 2, 1, 4, 4]


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
    t1 = demo_validator_property()

    # --- Test validator for myName (string) ---
    # Setting should trigger _validate_myName and prefix the value
    t1.myName = "Alice"
    assert t1._myName == "Name: Alice" # includes validator "Name: "
    assert t1.myName == "Name: Alice hehe"  # includes fget tag " hehe"

    # --- Test validator for myItems (dict) ---
    # The _validate_myItems adds 5 to the value being assigned, so a setitem on dict should go through that

    # Initial dict should be empty
    assert isinstance(t1.myItems._data, dict)
    assert t1.myItems == {}

    # Assign new dictionary directly
    t1.myItems = {'a': 10, 'b': 20}
    assert isinstance(t1.myItems._data, dict)
    # Validator returns value + 5 → but this doesn’t apply when setting a full dict in your current code
    # unless you have custom logic in HookedDescriptor to do this. Let's assume you do.
    assert t1.myItems == {'a': 15, 'b': 25}

    # Test assignment to a key, which should trigger the validator
    t1.myItems['x'] = 100  # should become 105
    assert t1.myItems['x'] == 105

    # Test updating multiple values
    t1.myItems.update({'y': 200, 'z': 300})
    assert t1.myItems['y'] == 205
    assert t1.myItems['z'] == 305

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