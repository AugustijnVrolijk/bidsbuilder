from bidsbuilder.schema.callback_property import CallbackField

def promote_to_callback(obj, attr_name):
    val = getattr(obj, attr_name)
    wrapper = CallbackField(val)
    setattr(obj, attr_name, wrapper)
    return wrapper
    
class demo_property():
    number = CallbackField(1)
    list1 = CallbackField([1,2])

def callback1(instance, val, old, new):
    print("hello")

def callback2(instance, val, old, new):
    print("ihhii")

t1 = demo_property()
#t1.number = CallbackField(t1.number)

demo_property.number.add_callback(t1, callback1)
demo_property.list1.add_callback(t1, callback2)
print(t1.number)
t1.number = 5
print(t1.number)
t1.number = 1
print(t1.number)

print(t1.list1)
t1.list1 = [4,3]
print(t1.list1)
t1.list1.append(1)
print(t1.list1)


"""
REQUIREMENTS, THINK ABOUT SUPPORT FOR A LIST (.append)

NEED TO TEST THE FOLLOWING:
    IF I CAN CALLBACK AN INSTANCE SPECIFIC METHOD,

    I.e. IF I can store the _check_schema of the correct instance as the callback method.. Or if I need to store datasetCore._check_schema(instance)

"""