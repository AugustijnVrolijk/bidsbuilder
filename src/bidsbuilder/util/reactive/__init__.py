from .descriptors import callback

from typing import Generic, TypeVar

T = TypeVar("T")

class CallbackField(Generic[T]):
    def __init__(self, *args, **kwargs):
        return

class singleCallbackField(Generic[T]):
    def __init__(self, *args, **kwargs):
        return

def wrap_callback_fields(*args, **kwargs):
    return


__all__ = ["callback", "singleCallbackField", "wrap_callback_fields"]
