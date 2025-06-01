
def get_property():
    return notImplemented()

def get_list_index():
    return notImplemented()

def wrap_list(*args):
    return notImplemented()

def contains():
    return notImplemented()

def op_and(a, b):
    return a and b

def op_or(a, b):
    return a or b

def notImplemented(*args, **kwargs):
    raise NotImplementedError()

__all__ = ["notImplemented", "get_property", "get_list_index", "wrap_list", "contains","op_and","op_or"]