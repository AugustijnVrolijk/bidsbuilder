from bidsbuilder.util.hooks.containers import *
import types
from bidsbuilder.util.hooks.new_containers import *

from typing import Union


def method1(self, a):
    print(a)
    return

class test1():
    def method2(self, a):
        print(f"hi {a}")
        return

class test2():
    def method3(self, a):
        print(f"hello {a}")
        return

def main():
    t1 = types.new_class("MyNewClass", (test1, test2), kwds={}, exec_body=lambda ns: ns.update({"method1": method1}))
 
    tester = t1()
    tester.method1("there")
    tester.method2("there")
    tester.method3("there")


if __name__ == "__main__":
    main()