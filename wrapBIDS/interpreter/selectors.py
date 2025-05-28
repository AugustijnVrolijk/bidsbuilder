import re
import operator as op
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
    @classmethod
    def from_raw(cls, r_selector:list[str]) -> 'selectorHook':

        funcs = []
        for selector in r_selector:
            parser = SelectorParser.from_raw(selector)
            abstrct_syntax_tree = parser.parse()
            func = selectorFunc(abstrct_syntax_tree)
            func.evaluate_static_nodes()
            funcs.append(func)

        return cls(funcs)

    def __init__(self, funcs):
        self.funcs = funcs
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

@define(slots=True, repr=False)
class selectorFunc:
    val: Any = field(repr=True)                                 #Can be a Callable, str, int, list, etc..
    args: list[Any] = field(repr=True, default=None)            #in the case it is a callable, defines the arguments to give it
    requires_input: bool = field(repr=False, default=False)     #Whether it needs the input datasetCore instance in the callable function
    n_required_args: int = field(repr=False, default=0) 
    is_callable: bool = field(repr=False, default=False) 

    def __str__(self):
        if self.is_callable:
            msg = ""
            if self.requires_input:
                msg = "datasetCore, "
            for arg in self.args:
                msg += f"{str(arg)}, "
            msg = msg[:-2]
            return f'{str(self.val.__name__)}({msg})'
        else:
            return str(self.val)

    def evaluate_static_nodes(self):
        return

    def __call__(self, *args):
        if not self.is_callable:
            return self.val
        
        if self.requires_input:
            final_args = args  
        else:
            final_args = []
 
        for arg in self.args:
            if isinstance(arg, selectorFunc):
                final_args.append(arg(*args))
            else:
                final_args.append(arg)

        return self.val(*final_args)

@dataclass
class token():
    val: str
    kind: str

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

    OPERATOR_FUNCS = {
        # function, how many arguments from LHS, how many arguments from RHS, enforce all RHS and LHS args equal the set limit
        "==":notImplemented,
        "!=":notImplemented,
        "<":notImplemented,
        ">":notImplemented,
        "<=":notImplemented,
        ">=":notImplemented,
        "in":notImplemented, #look at __contains__() in datasetCore then don't need to interpret function differently
        "!":notImplemented,
        """
        && and || as the grammar used in bids schema seems to show that they are conjoiners of seperate expressions
        i.e. '"SliceTiming" == sidecar.Unit || "AcquisitionDuration" in sidecar' refers to:
                   ("SliceTiming" in sidecar) OR ("AcquisitionDuration" in sidecar)
                                         rather than:
                   ("SliceTiming") in (sidecar OR ("AcquisitionDuration" in sidecar))             
        """
        "&&":notImplemented,
        "||":notImplemented,
        #".":notImplemented, special case where we will directly have logic to check for this in _resolve_field
        #"[]":notImplemented, special case where we will directly have logic to check for this in _resolve_field
        "-":notImplemented,
        "*":notImplemented,
        "/":notImplemented,
        }
    
    token_specification = [
                ('NUMBER',   r'\d+'),                               # Integer
                ('STRING',   r'"[^"]*"|\'[^\']*\''),                # String literals
                ('OP',       r'==|!=|<=|>=|\bin\b|[+\-*/\.<>]'),    # Operators
                ('LOGIC_OP', r'&&|\|\|'),                           # logic Operators
                ('ID',       r'[A-Za-z_]\w*'),                      # Identifiers
                ('LPAREN',   r'\('),                                # Left paren
                ('RPAREN',   r'\)'),                                # Right paren
                ('LBRACK',   r'\['),                                # Left bracket
                ('RBRACK',   r'\]'),                                # Right bracket
                ('SEP',      r'[, \t]+'),                           # Seperator - need to keep it so I can seperate brackets from indexing lists, to list definitions
                ('NOT',      r'!'),                                 # Not Operator - placed below OP so that != can be matched first
                ('MISMATCH', r'.'),                                 # Any other character
            ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokenizer = re.compile(tok_regex).match    
    nanToken = token(None, 'NONE')
    
    @classmethod
    def from_raw(cls, selector:str) -> 'SelectorParser':
        """
        used to instantiate a selectorParser from a raw string,
        so tokenises the input before returning an instance with the correct tokens
        """
        assert isinstance(selector, str), "from_raw needs a string as input"

        pos = 0
        tokens = []
        mo = cls.tokenizer(selector)
        while mo:
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'MISMATCH':
                raise RuntimeError(f'Unexpected character {value!r} at position {pos}')
            else:
                tokens.append(token(val=value, kind=kind))
            pos = mo.end()
            mo = cls.tokenizer(selector, pos)
        return cls(tokens)
 
    def __init__(self, tokens:list):
        self.tokens:list = tokens
        self.position:int = 0
        self.total:int = len(tokens)

    @classmethod
    def _build_syntax_tree(cls, selector):
        selector_tokens = cls._parse_tokens(selector)

        """
        RECURSIVELY CALL FUNCTIONS IN REVERSE ORDER OF THEIR PRECEDENCE

        TEMPLATE:

        Func level1():
            node = level2()
            while next_token and next_token.type is in level1.accepted_tokens:
                do some logic, in the case of and/or it would look like:
                if self.match("AND"):
                    op = operator.logical_and
                elif self.match("OR"):
                    op = operator.logical_or

                right_hand_side = level2()
                node = op(node, right_hand_side)
            return node

        where self.match looks a bit like

            match(*types):
                if self.next_token().type in types:
                    token = self.next_token.value
                    self.advance()
                    return token
                return None

            advance():
                self.position += 1
            
            next_token():
                return self.tokens[self.position]

        and self has attributes
            tokens : list of tokens (each token has a type and value)
            position : where along the list we are

        
        """


        return
    
    @property
    def cur_token(self) -> token:
        if self.position < self.total:
            return self.tokens[self.position]   
        return SelectorParser.nanToken
    
    @property
    def prev_token(self) -> token:
        return self.tokens[self.position - 1]

    def match(self, *types) -> token:
        if self.cur_token.val and (self.cur_token.kind in types):
            self.advance()
            return self.cur_token
        raise SyntaxError(f"Expected {types} but got {self.cur_token.kind}")

    def advance(self):
        self.position += 1
        if self.cur_token.kind == 'SEP':
            self.advance()

    def parse(self) -> selectorFunc:
        if self.position != 0:
            assert self.position == self.total, "SelectorParser did not fully parse selector"
            raise BufferError("Can only parse tokens once")
        return self.logic_term()
    
    def logic_term(self):
        node = self.additive_term()
        while self.cur_token.kind == "LOGIC_OP":
            if self.cur_token.val == "&&":
                val = op.and_
            elif self.cur_token.val == "||":
                val = op.or_
            else:
                raise RuntimeError(f"Unable to match token {self.cur_token} to logic_term()")
            
            self.match("LOGIC_OP")

            right = self.additive_term()
            node = selectorFunc(val=val, 
                                args=[node, right],
                                requires_input=False,
                                is_callable=True,
                                n_required_args=2)
        return node

    def additive_term(self):
        pass

    def factor(self):
        
        pass

if __name__ == "__main__":
    pass

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


True and False or False and True