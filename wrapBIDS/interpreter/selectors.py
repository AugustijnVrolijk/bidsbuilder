import re

from decorator import decorator
from collections.abc import Callable
from typing import Any, Tuple, Dict

from wrapBIDS.interpreter.evaluation_funcs import *
from wrapBIDS.interpreter.fields_funcs import *
from wrapBIDS.interpreter.operator_funcs import *


class selectorHook():
    def __init__(self, func:Callable):
        self.objectiveFunc = func
        return

    def __call__(self, *args, **kwargs):
        return self.objectiveFunc(*args, **kwargs)

class selectorFunc():
    def __init__(self, func:str, fglobals:dict, flocals:dict):
        if not isinstance(func, str) or not isinstance(fglobals, dict) or not isinstance(flocals, dict):
            raise TypeError(f"Wrong type for selectorFunc func: {func}\nglobals: {fglobals}\nlocals: {flocals}")
        
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
    "count":notImplemented,
    "exists":notImplemented,
    "index":notImplemented,
    "intersects":notImplemented,
    "allequal":notImplemented,
    "length":notImplemented, #consider using default len
    "match":notImplemented,
    "max":notImplemented,
    "min":notImplemented,
    "sorted":notImplemented,
    "substr":notImplemented,
    "type":notImplemented,
    }

    #considered using eval and then not needing to implement operator funcs
    #but this seemed slower and slightly unsafe with the possibility of interpreting
    #a function which imported global vars
    OPERATOR_FUNCS = {
        "==":notImplemented,
        "!=":notImplemented,
        "<":notImplemented,
        ">":notImplemented,
        "<=":notImplemented,
        ">=":notImplemented,
        "in":notImplemented, #look at __contains__() in datasetCore then don't need to interpret function differently
        "!":notImplemented,
        "&&":notImplemented,
        "||":notImplemented,
        #".":notImplemented, special case where we will directly have logic to check for this in _resolve_field
        #"[]":notImplemented, special case where we will directly have logic to check for this in _resolve_field
        "-":notImplemented,
        "*":notImplemented,
        "/":notImplemented
        }
    
    @classmethod
    def parseSelector(cls, r_selector:str) -> selectorFunc:
        """Main parser function
        
        splits functions into tokens, before assigning each token to the correct function
        Finally assigns the resolved functions to a callable selectorFunc instance
        """
        selector_tokens = cls._smart_split(r_selector)
        reformated_tokens = cls._reformat_op(selector_tokens)
        objective_func = cls._make_eval_string(reformated_tokens)
        fglobals, flocals = cls._getReferences(reformated_tokens)
        return selectorFunc(objective_func, fglobals, flocals)
    

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
    def _resolve_function(cls, s:str) -> tuple[str, list[str]]:
        assert s.startswith(")")

        function:str
        raw_arguments:str
        for i in range(len(s)):
            if s[i] == "(":
                function = s[:i]
                raw_arguments = s[(i+1):]
                break
        
        token_arguments = cls._smart_split(raw_arguments, ",")
        final_arguments:list = []
        for token in token_arguments:
            final_arguments.append(cls._resolve_field(token))

        function = cls.EVAL_FUNCS[function]
        return (function, final_arguments)
    
    @classmethod
    def _resolve_field(cls, s:str):
        #case 1: string is a unknown string, defined by ""
        if s.startswith(('"', "'")) and s.endswith(('"', "'")):
            return s[1:-1]

        #case 2: string has a .
        if s.find("."):
            pass
        else:
            return
        return cls.FIELDS_MAP[s]

    @staticmethod
    def _smart_split(s:str, splitter:str=" ") -> list[str]:
        #split based on whitespace
        tokens = s.split(splitter)

        #need to merge function calls, list comprehensions and seperate not: "!"
        final_tokens = []
        tokenLen = len(tokens)
        i = 0
        while i < tokenLen:
            cur = tokens[i]

            #check if I need to merge function
            if cur.count("(") != cur.count(")"):
                cur, new_i = SelectorParser._complete_token(tokens[i:], ["(",")"])
                i += new_i
                
            #check if I need to merge list
            elif cur.count("[") != cur.count("]"):
                cur, new_i = SelectorParser._complete_token(tokens[i:], ["[","]"])
                i += new_i

            #seperate not
            if cur[0] == '!' and cur[1] != "=":
                final_tokens.append(cur[0])
                cur = cur[1:]

            final_tokens.append(cur)
            i += 1

        return final_tokens

    @staticmethod
    def _complete_token(tokens:list[str], checkval:tuple[str, str]) -> tuple[str, int]:

        cur:str = ""
        for i in range(len(tokens)):
            cur += f" {tokens[i]}"
            if cur.count(checkval[0]) == cur.count(checkval[1]):
                return cur.strip(), i

        raise IndexError("couldn't complete sequence")
   

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


