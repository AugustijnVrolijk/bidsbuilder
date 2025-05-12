from typing import Any


class bidsEvalFunctions():
    @staticmethod
    def count(arg:list, val:Any) -> int:
        return

    @staticmethod
    def exists(arg:str|list, rule:str) -> int:
        val_rules = ["dataset", "subject", "stimuli", "file", "bids-uri"]
        if rule not in val_rules:
            raise ValueError(f"{rule} not a valid rules, please see https://bidsschematools.readthedocs.io/en/latest/description.html#the-exists-function")
        return
    
    @staticmethod
    def index():

        return

    @staticmethod
    def intersects():

        return

    @staticmethod
    def allequal():

        return

    @staticmethod
    def length():

        return

    @staticmethod
    def match():

        return

    @staticmethod
    def max():

        return

    @staticmethod
    def min():

        return

    @staticmethod
    def sorted():

        return

    @staticmethod
    def substr():

        return

    @staticmethod
    def nType():

        return

class bidsEvalExpressions():
   
    @staticmethod
    def path():
        #use posixpath(), has the same format that BIDS needs
        return

def notImplemented(*args, **kwargs):
    raise NotImplementedError()

count = bidsEvalFunctions.count
exists = bidsEvalFunctions.exists
index = bidsEvalFunctions.index
intersects = bidsEvalFunctions.intersects
allequal = bidsEvalFunctions.allequal
length = len
match = bidsEvalFunctions.match
max = bidsEvalFunctions.max
min = bidsEvalFunctions.min
sorted = bidsEvalFunctions.sorted
substr = bidsEvalFunctions.substr
nType = bidsEvalFunctions.nType

path = bidsEvalExpressions.path

__all__ = ["count", "exists", "index", "intersects", "allequal", "length", "match", "max", "min", "sorted", "substr", "nType", "path", "notImplemented"]