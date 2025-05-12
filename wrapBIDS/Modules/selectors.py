import re

from decorator import decorator
from collections.abc import Callable
from typing import Any, Tuple, Dict
from wrapBIDS.Modules.interpretedFunctions import *

class selectorHook():
    def __init__(self, func:Callable):
        self.objectiveFunc = func
        return

    def __call__(self, *args, **kwargs):
        return self.objectiveFunc(*args, **kwargs)



def resolveSelector():
    @decorator
    def inner(func, *args, **kwargs):
        
        return selectorHook(func)
    return inner


@resolveSelector
class selFunc():
    def __init__(self, func:str, fglobals:dict, flocals:dict):
        if not isinstance(func, str) or not isinstance(fglobals, dict) or not isinstance(flocals, dict):
            raise TypeError(f"Wrong type for selFunc func: {func}\nglobals: {fglobals}\nlocals: {flocals}")
        
        self.func = func
        self.fglobals = fglobals
        self.flocals = flocals

    def __call__(self) -> Any:
        return eval(self.func, globals=self.fglobals, locals=self.flocals)


class SelectorParser():
    FIELDS_MAP = {
    "schema": notImplemented,
    "dataset": notImplemented,
    "subject": notImplemented,
    "path": notImplemented,
    "entities": notImplemented,
    "datatype": notImplemented,
    "suffix": notImplemented,
    "extension": notImplemented,
    "modality": notImplemented,
    "sidecar": notImplemented,
    "associations": notImplemented,
    "columns": notImplemented,
    "json": notImplemented,
    "gzip": notImplemented,
    "nifti_header": notImplemented,
    "ome": notImplemented,
    "tiff": notImplemented,
    }

    EVAL_FUNCS = {
    "count":count,
    "exists":exists,
    "index":index,
    "intersects":intersects,
    "allequal":allequal,
    "length":length, #consider using default len
    "match":match,
    "max":max,
    "min":min,
    "sorted":sorted,
    "substr":substr,
    "type":nType,
    }

    OPERATOR_FUNCS = {
        #"==":"==",
        #"!=":"!=",
        #"<":"<",
        #">":">",
        #"<=":"<=",
        #">=":">=",
        #"in":"in", #look at __contains__() in datasetCore then don't need to interpret function differently
        "!":"not",
        "&&":"and",
        "||":"or",
        #".":"",
        #"[]":"",
        #"-":"-",
        #"*":"*",
        #"/":"/"
        }
    
    @classmethod
    def _reformat_op(cls, raw_str:list[str])-> list[str]:
        reformated = []
        for token in raw_str:
            if token in cls.OPERATOR_FUNCS.keys():
                token = cls.OPERATOR_FUNCS[token]
            reformated.append(token)

        return reformated
    
    @classmethod
    def _find_matching_key(cls, string:str) -> str|None:
        for key in cls.EVAL_FUNCS.keys():
            if key in string:
                return key
        return None

    @classmethod
    def parse_function_inputs(cls, func_str: str, key: str) -> dict:
        if not func_str.startswith(key + "(") or not func_str.endswith(")"):
            raise ValueError("Function string doesn't start with the expected key.")
        
        # Remove the key and outer parentheses
        inner = func_str[len(key) + 1:-1]

        # Split on commas and strip spaces
        parts = [part.strip() for part in inner.split(',')]

        flocals = {}
        for part in parts:
            if part in cls.FIELDS_MAP.keys():
                flocals[part] = cls._find_field_ref(part)

        return flocals

    @classmethod
    def _find_field_ref() -> Any:
        """
          PARSE ANY FIELD_MAP KEYS WITHIN THE FUNCTION EVAL STRING:
                    I.E:    intersects(dataset.modalities, ["pet", "mri"]) NEEDS TO FIND THE REFERENCE TO "dataset.modalities"           
                """
        return
        
    @classmethod
    def _getReferences(cls, str_tokens:str) -> Tuple[Dict, Dict]:
        fglobals = {}
        flocals = {}

        for token in str_tokens:
            """
            need to first pre-process token
            i.e. check if it is a func:
                get the right function - (careful edge cases, 'sorted(sidecar.VolumeTiming)' returns function = min atm with the simple in)
                
            check if func (is there a '(' and ')' pair)
                if so split on those as well as any spaces and commas inside

                first val is the fglobal value

                rest of values run through find field ref

            find field ref:
                need to split on . and [] and then process based on that, i.e. if it is present then its a field ref and need to find how to process it based on that dict
            """


            if token in cls.FIELDS_MAP.keys():
                flocals[token] = cls._find_field_ref(token)
            else:

                key = cls._find_matching_key(token)
                if key:
                    fglobals[key] = cls.EVAL_FUNCS[key]
                    flocals.update(cls.parse_function_inputs(token, key))
        return fglobals, flocals
    
    @classmethod
    def parseSelector(cls, r_selector:str) -> selFunc:
        selector_tokens = SelectorParser._smart_split(r_selector)
        reformated_tokens = cls._reformat_op(selector_tokens)
        objective_func = cls._make_eval_string(reformated_tokens)
        fglobals, flocals = cls._getReferences(reformated_tokens)
        return selFunc(objective_func, fglobals, flocals)
    
    @staticmethod
    def _make_eval_string(string_tokens:list) -> str:
        return " ".join(string_tokens)

    @staticmethod
    def _smart_split(s):
        tokens = re.findall(r'\w+\(.*?\)|[^\s()]+', s)
                
        final_tokens = []
        for token in tokens:
            if len(token) > 1:
                if token[0] == '!' and token[1] != "=":
                    final_tokens.append(token[0])
                    final_tokens.append(token[1:])
                else:
                    final_tokens.append(token)
                if token.count("(") != token.count(")"):
                    raise RuntimeError(f"Bug during regex _smart_split on {s}\n split into: {tokens}")
            else:
                final_tokens.append(token)

        return final_tokens
   

def tester():
    return

if __name__ == "__main__":
    tester()

"""
OPERATOR_FUNCS = {
    '==': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    'in':"",
    "!":"",
    "&&":"",
    "||":"",
    ".":"",
    "[]":"",
    "+":operator.add,
    "-":operator.sub,
    "*":operator.mul,
    "/":operator.truediv,
    }
"""


