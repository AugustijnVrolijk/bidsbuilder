from bidsbuilder.util.hooks.containers import *

from abc import ABC

class MyABC(ABC):
    forbidden_names = {"do_not_use", "bad_attr"}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name in cls.forbidden_names:
            if name in cls.__dict__:
                raise TypeError(
                    f"Class {cls.__name__} must not define `{name}` "
                    f"(reserved by {MyABC.__name__})."
                )

class BadImpl1(MyABC):
    do_not_use = 123  # 🚨 raises TypeError at definition

class BadImpl2(MyABC):
    def bad_attr(self):  # 🚨 also raises TypeError
        pass

class GoodImpl(MyABC):
    x = 42  # ✅ allowed