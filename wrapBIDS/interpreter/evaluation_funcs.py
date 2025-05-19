from typing import Any


def count(arg:list, val:Any) -> int:
    return

def exists(arg:str|list, rule:str) -> int:
    val_rules = ["dataset", "subject", "stimuli", "file", "bids-uri"]
    if rule not in val_rules:
        raise ValueError(f"{rule} not a valid rules, please see https://bidsschematools.readthedocs.io/en/latest/description.html#the-exists-function")
    return

def index():

    return

def intersects():

    return

def allequal():

    return

def length():

    return

def match():

    return

def max():

    return

def min():

    return

def sorted():

    return

def substr():

    return

def nType():

    return

__all__ = ["count", "exists", "index", "intersects", "allequal", "length", "match", "max", "min", "sorted", "substr", "nType"]