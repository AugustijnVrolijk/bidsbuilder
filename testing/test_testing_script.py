from bidsbuilder.util.hooks.containers import *
import types
from bidsbuilder.util.hooks.new_containers import *

from typing import Union


def method1(self, a):
    print(a)
    return

class test1():
    __slots__ = ["var1", "var2"]
    def method2(self, a):
        print(f"hi {a}")
        return


def inherit_class(to_inherit):
    class to_inherit(test1):
        ...

    
    return to_inherit

def main():
    t1 = types.new_class("MyNewClass", (), kwds={}, exec_body=lambda ns: ns.update({"method1": method1, "__slots__":["var3", "var4"]}))
 
    tester = t1()
    tester.method1("there")
    #tester.method2("there")
    test2 = inherit_class(t1)

    tester.var3 = 10
    tester.var4 = 20

    print(tester.__dict__)


    tester2 = test2()
    tester2.var1 = 5
    tester2.var2 = 10
    tester2.var3 = 15
    tester2.var4 = 20

    print(tester2.__dict__)


if __name__ == "__main__":
    main()