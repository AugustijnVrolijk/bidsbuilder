import attrs
from attrs import define, field


@define(slots=True)
class testBase:

    val1:int = field(repr=True)
    def __attrs_post_init__(self):
        print("testBase __attrs_post_init__ called")
        """Post-initialization hook for testBase."""
        self.val1 += 10
    pass


@define(slots=True)
class inherit1(testBase):
    
    val2:int = field(repr=True)
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        """Post-initialization hook for inherit1."""
        print("inherit1 __attrs_post_init__ called")
        self.val2 += 5

@define(slots=True)
class inherit2(inherit1):
    """This class inherits from inherit1 and can have additional attributes or methods."""
    
    val3:int = field(repr=True)
    
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        """Post-initialization hook for inherit2."""
        print("inherit2 __attrs_post_init__ called")
        self.val3 += 3

t = inherit1(val1=1, val2=2)
print(t)

t2 = inherit2(val1=1, val2=2, val3=3)
print(t2)