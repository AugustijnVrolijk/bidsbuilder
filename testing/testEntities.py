import attrs
from attrs import define, field


@define(slots=True)
class testBase:

    val1:int = field(repr=True)
    def __attrs_post_init__(self):
        print("testBase __attrs_post_init__ called")
        """Post-initialization hook for testBase."""
        self.val1 += 10
    
    @property
    def val(self):
        """Public getter for val1."""
        return self.val1 * 1.5

    @val.setter
    def val(self, new_val:int):
        print("originl setter called")
        return

@define(slots=True)
class inherit1(testBase):
    
    val2:int = field(repr=True)
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        """Post-initialization hook for inherit1."""
        print("inherit1 __attrs_post_init__ called")
        self.val2 += 5

    @testBase.val.setter
    def val(self, new_val:int):
        """Setter for val, which is not used in this example."""
        print(f"Setting val to {new_val}, inherit 1")
        self.val1 = new_val

@define(slots=True)
class inherit2(inherit1):
    """This class inherits from inherit1 and can have additional attributes or methods."""
    
    val3:int = field(repr=True)
    
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        """Post-initialization hook for inherit2."""
        print("inherit2 __attrs_post_init__ called")
        self.val3 += 3

    @testBase.val.setter
    def val(self, new_val:int):
        """Setter for val, which is not used in this example."""
        print(f"Setting val to {new_val}, inherit 2")
        self.val1 = new_val / 10

t = inherit1(val1=1, val2=2)
print(t)

t2 = inherit2(val1=1, val2=2, val3=3)
print(t2)

print(t2.val)  # Should print 110 (1 + 10) * 10
t2.val = 512
print(t2.val)  # Should print 5120 (512 + 10) * 10

print(t.val)
t.val = 100
print(t.val)  # Should print 165.0 (100 + 10) * 1.5


t = set()
t2 = set()

t.add(1)
t.add(2)
t.add(3)    
t2.add(5)
t2.add(6)
t2.add(8)

print(t.union(t2))  # Should print {1, 2, 3, 5, 6, 8}