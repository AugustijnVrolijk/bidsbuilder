import re

from functools import wraps
from collections.abc import Callable
from typing import Any, Tuple, Union, TYPE_CHECKING, Optional

from wrapBIDS.interpreter.evaluation_funcs import *
from wrapBIDS.interpreter.fields_funcs import *
from wrapBIDS.interpreter.operator_funcs import *
from dataclasses import dataclass
from attrs import define, field

if TYPE_CHECKING:
    from wrapBIDS.modules.coreModule import DatasetCore

class selectorHook():
    def __init__(self):
        self.funcs = []
        return

    def __call__(self, *args, **kwargs):
        return all(func(*args, **kwargs) for func in self.funcs)

def feedListOfStr(func):
    """
    expands list to feed them as single values to function
    """
    @wraps(func)
    def wrapper(*args):
        if isinstance(args[0], list) and len(args) == 1:
            final = []
            for sub_str in args[0]:
                assert isinstance(sub_str, str)
                if not sub_str:
                    continue
                final.append(func(sub_str.strip()))
            return tuple(final)
        else:
            return func(*args)
    return wrapper

@dataclass
class evalNode:
    val: Any = None #Can be a Callable, str, int, list, etc..
    args: Union[Any] = None #in the case it is a callable, defines the arguments to give it
    is_leaf: bool = None 
    requires_input: bool = None
    is_callable: bool = None
    parent: Optional["evalNode"] = None

@define(slots=True)
class selectorFunc():

    func:evalNode = field(repr=False)

    def __call__(self, caller:"DatasetCore") -> Any:
        return 

    def evaluate_static_nodes(self) -> None:
        return 

    def _recursive_run(self, func:Callable, args:list[Any]) -> Any:
        #check if args is a function

        #if it is, reassign args to the output of that call
        
        return

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
        # function, how many arguments from LHS, how many arguments from RHS, enforce all RHS and LHS args equal the set limit
        "==":(notImplemented,1,1,False),
        "!=":(notImplemented,1,1,False),
        "<":(notImplemented,1,1,False),
        ">":(notImplemented,1,1,False),
        "<=":(notImplemented,1,1,False),
        ">=":(notImplemented,1,1,False),
        "in":(notImplemented,1,1,False), #look at __contains__() in datasetCore then don't need to interpret function differently
        "!":(notImplemented,0,1,False),
        """
        && and || are "True" as the grammar used in bids schema seems to show that they are conjoiners of seperate expressions
        i.e. '"SliceTiming" == sidecar.Unit || "AcquisitionDuration" in sidecar' refers to:
                   ("SliceTiming" in sidecar) OR ("AcquisitionDuration" in sidecar)
                                         rather than:
                   ("SliceTiming") in (sidecar OR ("AcquisitionDuration" in sidecar))             
        """
        "&&":(notImplemented,1,1,True),
        "||":(notImplemented,1,1,True),
        #".":notImplemented, special case where we will directly have logic to check for this in _resolve_field
        #"[]":notImplemented, special case where we will directly have logic to check for this in _resolve_field
        "-":(notImplemented,1,1,False),
        "*":(notImplemented,1,1,False),
        "/":(notImplemented,1,1,False)
        }
    
    @classmethod
    def createSelector(cls, r_selector:list[str]) -> selectorHook:
        """Main parser function
        
        splits functions into tokens, before assigning each token to the correct function
        Finally assigns the resolved functions to a callable selectorFunc instance
        """

        final = selectorHook()
        for selector in r_selector:
            syntax_tree = cls._build_syntax_tree(selector)
            func = selectorFunc(syntax_tree)
            func.evaluate_static_nodes()
            final.funcs.append(func)

        return final
    
    @classmethod
    def _build_syntax_tree(cls, selector):

        """
        iterate, but do a breadth first rather than depth first.
        Possibly have a stack of nodes to evaluate

        FIRST PHASE = PARSE THE SELECTOR INTO A NESTED LIST AND TOKENISE ACCORDING TO GRAMMAR, I.E. LABEL BASED ON FUNCTION (operator, callable, int, str, list, field, etc..)

        SECOND PHASE = INTERPRET THE PARSED LIST AND GENERATE THE EVAL NODES OUT OF THEM USING GRAMMAR RULES

        """

        selector_tokens = cls._parse_selector(selector)
        
        while len(tree) != 1:
            for i,token in enumerate(tokens):
                t_token, flag = cls._resolve_token(token)
                #flag is 1 if it is an operator, and 0 if it is a operand (callable function or field)
                if not flag:
                    tree.append(t_token)
                    continue
                #unpack tuple for operators
                t_token, LHS, RHS, enforce = t_token


        return

    @classmethod
    def _parse_selector(cls, selector) -> list[Any]:
        tokens = []
        cur_tok = ""
        for letter in selector:
            
        return

    @classmethod
    def _resolve_token(cls, token:str) -> Tuple[Union[list, str], int]:
        #resolve token and return a flag if it is an operand or operator
        #flag of 0 is resolved function or field, 1 is unresolved operator

        if "(" in token:
            assert ")" in token
            output = cls._resolve_function(token)
            flag = 0
        
        elif token in cls.OPERATOR_FUNCS.keys():
            output = cls.OPERATOR_FUNCS[token]
            flag = 1

        else:
            output = cls._resolve_field(token)
            flag = 0
        
        return (output, flag)
    
    @classmethod
    def _resolve_function(cls, s:str) -> Tuple[str, list[str]]:
        assert s.endswith(")")
        s = s[:-1]

        function:str
        raw_arguments:str
        for i in range(len(s)):
            if s[i] == "(":
                function = s[:i]
                raw_arguments = s[(i+1):]
                break
        
        token_arguments = cls._smart_split(raw_arguments, ",")
        final_arguments:list = cls._resolve_field(token_arguments)

        function = cls.EVAL_FUNCS[function]
        return (function, final_arguments)
    
    @classmethod
    @feedListOfStr
    def _resolve_field(cls, s:str) -> Tuple[Union[Tuple[Callable, str], Callable,str], Union[Tuple[int, int], int]]:
        s = s.strip()
        #case 1: string is a unknown string, defined by ""
        if s.startswith(('"', "'")) and s.endswith(('"', "'")):
            """
            Need to check for integers and covnvert them accordingly
            """
            return s[1:-1]

        #case 2: string has a .
        if "." in s:
            tokens = s.split(".")
            assert len(tokens) == 2
            return ((cls.FIELDS_MAP[tokens[0]], tokens[1]), ())
        
        #case 3: string has a []
        if ("[" in s) and ("]" in s):
            assert s.startswith('[') and s.endswith(']')
            s = s[1:-1]
            tokens = re.split(r"[ ,]", s)
            return cls._resolve_field(tokens)
        
        #final case, its just in the field map
        return cls.FIELDS_MAP[s]

    @staticmethod
    def _smart_split(s:str) -> list[str]:
        #split based on whitespace
        tokens = re.split(r'[ ,]+', s)
        #need to merge function calls, list comprehensions and seperate not: "!"
        final_tokens = []
        tokenLen = len(tokens)
        i = 0
        while i < tokenLen:
            cur = tokens[i]

            #seperate not
            if cur[0] == '!' and cur[1] != "=":
                final_tokens.append(cur[0])
                cur = cur[1:]

            #check if I need to merge function
            if cur.count("(") != cur.count(")"):
                cur, new_i = SelectorParser._complete_token(cur, tokens[(i+1):], ["(",")"])
                i += new_i
                
            #check if I need to merge list
            elif cur.count("[") != cur.count("]"):
                cur, new_i = SelectorParser._complete_token(tokens[(i+1):], ["[","]"])
                i += new_i

            final_tokens.append(cur)
            i += 1

        return final_tokens

    @staticmethod
    def _complete_token(cur:str, tokens:list[str], checkval:Tuple[str, str]) -> Tuple[str, int]:
        #MERGES TOKENS BACK TO ENSURE () or [] ARE KEPT TOGETHER
        #MERGES USING ' ', whitespace
        for i in range(len(tokens)):
            cur += f" {tokens[i]}"
            if cur.count(checkval[0]) == cur.count(checkval[1]):
                return cur.strip(), (i+1)

        raise IndexError("couldn't complete sequence")

    @classmethod
    def _check_syntax(cls, token:str):
        """ CAN CHECK FOR SYNTAX; ENSURE THAT TOKENS HAVE EQUAL NUMBERS OF ( to ), or [ to ] etc.., IF A STRING HAS 'before and After' """
        return    
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


