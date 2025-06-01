from typing import Any


def count(arg:list, val:Any) -> int:
    return notImplemented()

def exists(arg:str|list, rule:str) -> int:
    val_rules = ["dataset", "subject", "stimuli", "file", "bids-uri"]
    if rule not in val_rules:
        raise ValueError(f"{rule} not a valid rules, please see https://bidsschematools.readthedocs.io/en/latest/description.html#the-exists-function")
    
    return notImplemented()

def index():

    return notImplemented()

def intersects():

    return notImplemented()

def allequal():

    return notImplemented()

def length():

    return notImplemented()

def match():

    return notImplemented()

def max():

    return notImplemented()

def min():

    return notImplemented()

def sorted():

    return notImplemented()

def substr():

    return notImplemented()

def nType():

    return notImplemented()

def notImplemented(*args, **kwargs):
    raise NotImplementedError()

__all__ = ["count", "exists", "index", "intersects", "allequal", "length", "match", "max", "min", "sorted", "substr", "nType"]

