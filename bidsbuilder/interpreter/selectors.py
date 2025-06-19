import re
import operator as op
from typing import Any, TYPE_CHECKING, Callable

from .evaluation_funcs import *
from .fields_funcs import *
from .operator_funcs import *
from dataclasses import dataclass
from attrs import define, field

if TYPE_CHECKING:
    from bidsbuilder.modules.coreModule import DatasetCore

@define(slots=True, repr=True)
class selectorHook():
    funcs: list[Callable] = field(repr=False)
    _original: list[str] = field(repr=True, alias="_original")

    def __str__(self) -> str:
        msg = ""
        for i, val in enumerate(self._original):
            msg += f"orig: '{val}'\nfunc: {str(self.funcs[i])}"

        return msg
  
    @classmethod
    def from_raw(cls, r_selector:list[str]) -> 'selectorHook':
        if not isinstance(r_selector, list):
            r_selector = [r_selector]

        funcs = []
        for selector in r_selector:
            parser = SelectorParser.from_raw(selector)
            sel_function = parser.parse()
            sel_function.evaluate_static_nodes()
            funcs.append(sel_function)

        return cls(funcs, r_selector)
    
    def __call__(self, *args, **kwargs):

        #all(func(*args, **kwargs) for func in self.funcs) can be slower
        for func in self.funcs:
            if not func(*args, **kwargs):
                return False
        return True

@define(slots=True, repr=False)
class selectorFunc:
    val: Any = field(repr=False)                                 #Can be a Callable, str, int, list, etc..
    args: list[Any] = field(repr=False, default=[])            #in the case it is a callable, defines the arguments to give it
    requires_input: bool = field(repr=False, default=False)     #Whether it needs the input datasetCore instance in the callable function
    is_callable: bool = field(repr=False, default=False) 

    def __str__(self) -> str:
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

    def evaluate_static_nodes(self) -> bool:
        args_static = True
        for i,func in enumerate(self.args):
            if isinstance(func, selectorFunc):
                if func.evaluate_static_nodes():
                    self.args[i] = func()
                else:
                    args_static = False

        if args_static and (not self.requires_input):
            self.val = self.__call__()
            self.is_callable = False
            return True
        return False

    def __call__(self, *args:'DatasetCore') -> Any:
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
    """
    Selector Parser is a recursive descent parser to interpret BIDS schema logic into executable python functions

    It includes a from_raw() method enabling tokenisation and parsing from the raw string expression
    """
    token_specification = [
                ('NUMBER',   r'\d+'),                               # Integer
                ('STRING',   r'"[^"]*"|\'[^\']*\''),                # String literals
                ('EQ_OP',    r'==|!=|<=|>=|\bin\b|[<>]'),           # Equality operators
                ('ADD_OP',   r'[+\-]'),                             # Additive operators
                ('MULT_OP',  r'[*/]'),                              # Multiplicative operators
                ('LOGIC_OP', r'&&|\|\|'),                           # logic Operators
                ('ID',       r'[A-Za-z_]\w*'),                      # Identifiers
                ('LPAREN',   r'\('),                                # Left paren
                ('RPAREN',   r'\)'),                                # Right paren
                ('LBRACK',   r'\['),                                # Left bracket
                ('RBRACK',   r'\]'),                                # Right bracket
                ('SEP',      r'[, \t]+'),                           # Seperator - need to keep it so I can seperate brackets from indexing lists, to list definitions
                ('UNARY',    r'!'),                                 # Unary ops - placed below OP so that != can be matched first
                ('DOT',      r'\.'),                                # Subscription operator
                ('MISMATCH', r'.'),                                 # Any other character
            ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokenizer = re.compile(tok_regex).match    
    nanToken = token(None, 'NONE')
    
    @classmethod
    def from_raw(cls, selector:str|None) -> 'SelectorParser':
        """
        used to instantiate a selectorParser from a raw string,
        so tokenises the input before returning an instance with the correct tokens
        """
        #bidsschematools already parses some statements? i think...
        #using the provided load_schema returns expressions where "null" is already None...
        #convert this back to ensure no errors in this parser.
        if selector is None:
            selector = "null"

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

    @property
    def cur_token(self) -> token:
        if self.position < self.total:
            return self.tokens[self.position]   
        return SelectorParser.nanToken
    
    @property
    def prev_token(self) -> token:
        return self.tokens[self.position - 1]

    @property
    def next_token(self) -> token:
        if (self.position + 1) < self.total:
            return self.tokens[(self.position+1)]
        return SelectorParser.nanToken

    def match(self, *types) -> Any:
        cur = self.cur_token
        if cur.val and (cur.kind in types):
            self.advance()
            return cur.val
        raise SyntaxError(f"Expected {types} but got {self.cur_token.kind}")

    def advance(self):
        self.position += 1
        if self.cur_token.kind == 'SEP':
            self.advance()

    def parse(self) -> selectorFunc:
        if self.position != 0:
            assert self.position == self.total, "SelectorParser did not fully parse selector"
            raise BufferError("Can only parse tokens once")
        
        syntax_tree = self.logic_term()
        if self.position != self.total:
            raise IndexError("Wasn't able to fully parse input expression")

        return syntax_tree
    
    LOGIC_OPS = {
        "&&":op_and, #possibly look at defining a small function, as currently 
        "||":op_or,  #calling .__name__ on the handle returns <lambda>
    }

    def logic_term(self):
        node = self.equality_term()

        #USE IF HERE AND WHILE AFTER
        #THIS ENFORCES DETERMINISTIC BEHAVIOUR AND FORCES USER TO DEFINE COMBINATIONS
        #OF AND & OR USING (parentheses)
        if self.cur_token.kind == "LOGIC_OP":
            val = self.LOGIC_OPS[self.cur_token.val]
            if self.cur_token.val == "&&":
                cur_type = "&&"
                other = "||"
            elif self.cur_token.val == "||":
                cur_type = "||"
                other = "&&"
            else:
                raise RuntimeError(f"Unable to match token {self.cur_token} to logic_term()")

            #CAN MATCH MULTIPLE OF THE SAME TYPE DETERMINISTICALLY, A AND B AND C, is always the same
            #similarly, A OR B OR C IS ALWAYS THE SAME; BUT A AND B OR C IS DIFFERENT IF 
            # INTERPRETED (A AND B) OR C - or - A AND (B OR C)            
            while self.cur_token.val == cur_type:
                self.match("LOGIC_OP")
                right = self.equality_term()
                node = selectorFunc(val=val, 
                                    args=[node, right],
                                    requires_input=False,
                                    is_callable=True)
        
            if self.cur_token.val == other:
                raise ValueError(f"Error parsing {self.cur_token} - To chain multiple logical operators use parentheses to define the order")

        return node
    
    EQ_OPS = {
        "==":op.eq,
        "!=":op.ne,
        "<":op.lt,
        ">":op.gt,
        "<=":op.le,
        ">=":op.ge,
        "in":contains, #look at __contains__() in datasetCore then don't need to interpret function differently
    }

    def equality_term(self):
        node = self.additive_term()

        #if instead of while as only a single comparator in a row is accepted: A == B <= C will not be interpreted and result in an error
        if self.cur_token.kind == "EQ_OP":
            val = self.EQ_OPS[self.cur_token.val]

            self.match("EQ_OP")
            right = self.additive_term()
            node = selectorFunc(val=val, 
                                args=[node, right],
                                requires_input=False,
                                is_callable=True)
        
        #If second chained comparator is found, throws an error
        if self.cur_token.kind == "EQ_OP":
            raise ValueError(f"Error parsing {self.cur_token} - Comparisons cannot be chained")

        return node

    ADD_OPS = {
        "-":op.sub,
        "+":op.add,
    }

    def additive_term(self):
        node = self.mult_term()

        #chained according to pemdas from left to right (used for -)
        while self.cur_token.kind == "ADD_OP":
            val = self.ADD_OPS[self.cur_token.val]

            self.match("ADD_OP")
            right = self.mult_term()
            node = selectorFunc(val=val, 
                                args=[node, right],
                                requires_input=False,
                                is_callable=True)
                
        return node

    MULT_OPS = {
        "*":op.mul,
        "/":op.truediv,
    }

    def mult_term(self):
        node = self.unary_term()

        #chained according to PEMDAS from left to right
        while self.cur_token.kind == "MULT_OP":
            val = self.MULT_OPS[self.cur_token.val]

            self.match("MULT_OP")
            right = self.unary_term()
            node = selectorFunc(val=val, 
                                args=[node, right],
                                requires_input=False,
                                is_callable=True)
        
        return node

    UNARY_OPS = {
        "!":op.not_,
        "-":op.neg,
        "+":op.pos,
        }
    
    def unary_term(self):

        if self.cur_token.kind in ["UNARY","ADD_OP"]:
            val = self.UNARY_OPS[self.cur_token.val]

            self.match("UNARY", "ADD_OP")
            right = self.unary_term() #right associative
            return selectorFunc(val=val, 
                                args=[right],
                                requires_input=False,
                                is_callable=True)
        else:
            return self.postfix_term()
        
    POSTFIX_OPS = {
        ".":get_property,
        "[":get_list_index,     
    }

    def postfix_term(self):
        node = self.primary()

        #chained according to PEMDAS from left to right
        while self.cur_token.val in self.POSTFIX_OPS.keys() and self.prev_token.kind == "ID":
            cur = self.cur_token
            if cur.val == ".":
                self.match("DOT")
                #INITIALLY TRIED right = self.primary() BUT:
                #Some subfields have the same name as the functions, i.e.
                #columns.type, where type refers to a parameter of the columns object,
                #Not the type() function
                right = self.match("ID")

            else:
                self.match("LBRACK")
                right = self.primary()
                self.match("RBRACK")

            val = self.POSTFIX_OPS[cur.val]

            node = selectorFunc(val=val, 
                                args=[node, right],
                                requires_input=False,
                                is_callable=True)
        
        return node

    FIELDS_MAP = {
    "schema": schema,
    "dataset": dataset,
    "subject": subject,
    "path": path,
    "entities": entities,
    "entity": entities, #there are some inconsistencies in the schema, using entity. instead of entities.
    "datatype": datatype,
    "suffix": suffix,
    "extension": extension,
    "modality": modality,
    "sidecar": sidecar,
    "associations": associations,
    "columns": columns,
    "json": json,
    "gzip": gzip,
    "nifti_header": nifti_header,
    "ome": ome,
    "tiff": tiff,
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

    def primary(self):
        cur = self.cur_token

        if cur.kind == "NUMBER":
            val = self.match("NUMBER")
            return int(val)
        
        elif cur.kind == "STRING":
            val = self.match("STRING")
            #need to trim outer " " or ' '
            return val[1:-1]
        
        elif cur.kind == "LPAREN":
            self.match("LPAREN")
            node = self.logic_term()
            self.match("RPAREN")
            return node
        
        elif cur.kind == "LBRACK":
            assert self.prev_token.kind != "ID", f"parsing logic thinks {cur} is a list, but context suggests it's an index"
            args = []
            self.match("LBRACK")
            #can have multiple items
            while self.cur_token.val and (self.cur_token.kind != "RBRACK"):
                args.append(self.additive_term())
            self.match("RBRACK")
            return selectorFunc(val=wrap_list, # list is wrong, this will break as the arguments will be passed in as list(arg1, arg2, ...)
                                #need to change it to a custom function which builds a list from a series of inputs
                                #can't wrap the args in another [] as need to recurse through the arguments to see if they need to be executed
                                args=args,  
                                requires_input=False,
                                is_callable=True)
        
        elif cur.kind == "ID":
            self.match("ID")
            if cur.val in self.FIELDS_MAP.keys():
                return selectorFunc(val=self.FIELDS_MAP[cur.val],
                                    requires_input=True,
                                    is_callable=True)
                 
            elif cur.val in self.EVAL_FUNCS.keys():
                self.match("LPAREN")
                args = []
                #can have multiple arguments
                while self.cur_token.val and (self.cur_token.kind != "RPAREN"):
                    args.append(self.additive_term())
                self.match("RPAREN")
                if cur.val == "exists":
                    return selectorFunc(val=self.EVAL_FUNCS[cur.val],
                                    args=args,
                                    requires_input=True,
                                    is_callable=True)
                
                return selectorFunc(val=self.EVAL_FUNCS[cur.val],
                                    args=args,
                                    requires_input=False,
                                    is_callable=True)
            
            elif cur.val == "null":
                return None
            else:
                return cur.val
        
        else:
            raise TypeError(f"Unable to match token {cur}")