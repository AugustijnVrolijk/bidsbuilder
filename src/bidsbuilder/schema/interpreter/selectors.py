import re
import operator as op
from typing import Any, TYPE_CHECKING, Callable

from .evaluation_funcs import *
from .fields_funcs import *
from .operator_funcs import *
from dataclasses import dataclass
from attrs import define, field

if TYPE_CHECKING:
    from bidsbuilder.modules.core.dataset_core import DatasetCore

@define(slots=True, repr=True)
class selectorHook():
    funcs: list[Callable] = field(repr=False)
    original: list[str] = field(repr=True)
    tags: set[str] = field(factory=set)

    def __str__(self) -> str:
        msg = ""
        for i, val in enumerate(self.original):
            msg += f"orig: '{val}'\nfunc: {str(self.funcs[i])}"

        return msg
  
    @classmethod
    def from_raw(cls, r_selector:list[str]) -> 'selectorHook':
        if not isinstance(r_selector, list):
            r_selector = [r_selector]

        funcs = []
        tags = set()
        for selector in r_selector:
            sel_function = SelectorParser.from_raw(selector)
            tags = set.union(tags, sel_function.tags)
            funcs.append(sel_function)

        selHook = cls(funcs, r_selector)
        selHook.tags = tags
        return selHook
    
    def __call__(self, *args, **kwargs):
        #all(func(*args, **kwargs) for func in self.funcs) can be slower
        
        for func in self.funcs:            
            if not func(*args, **kwargs):
                return False
        return True

@define(slots=True, repr=False)
class selectorFunc:
    val: Any = field(repr=False)                                 #Can be a Callable, str, int, list, etc..
    args: list[Any] = field(repr=False, factory=list)            #in the case it is a callable, defines the arguments to give it
    requires_input: bool = field(repr=False, default=False)     #Whether it needs the input datasetCore instance in the callable function
    is_callable: bool = field(repr=False, default=False) 

    tags: set = field(init=False, repr=True, factory=set) # tags which "fields" this selector func has
    # allows for optimisation when checking schema later by skipping irrelevant selectors

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

    def __call__(self, *args:'DatasetCore', **kwargs) -> Any:
        if not self.is_callable:
            return self.val
        
        add_callbacks = kwargs.get("add_callbacks", False)

        args_to_add = []

        if self.requires_input:
            final_args = list(args)
        else:
            final_args = []
 
        for arg in self.args:
            if isinstance(arg, selectorFunc):
                final_args.append(arg(*args, **kwargs))
            else:
                final_args.append(arg)

        if self.requires_input:
            return self.val(*final_args, add_callbacks=add_callbacks)
        else:
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
                ('NUMBER',   r'\d+'),                       # Integer
                ('STRING',   r'"[^"]*"|\'[^\']*\''),        # String literals
                ('EQ_OP',    r'==|!=|<=|>=|\bin\b|[<>]'),   # Equality operators
                ('ADD_OP',   r'[+\-]'),                     # Additive operators
                ('MULT_OP',  r'[*/]'),                      # Multiplicative operators
                ('LOGIC_OP', r'&&|\|\|'),                   # logic Operators
                ('BOOL',     r'false|true'),                # Bool values
                ('ID',       r'[A-Za-z_]\w*'),              # Identifiers
                ('LPAREN',   r'\('),                        # Left paren
                ('RPAREN',   r'\)'),                        # Right paren
                ('LBRACK',   r'\['),                        # Left bracket
                ('RBRACK',   r'\]'),                        # Right bracket
                ('SEP',      r'[, \t]+'),                   # Seperator - need to keep it so I can seperate brackets from indexing lists, to list definitions
                ('UNARY',    r'!'),                         # Unary ops - placed below OP so that != can be matched first
                ('DOT',      r'\.'),                        # Subscription operator
                ('MISMATCH', r'.'),                         # Any other character
            ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokenizer = re.compile(tok_regex).match    
    nanToken = token(None, 'NONE')
    
    @classmethod
    def from_raw(cls, selector:str|None) -> 'selectorFunc':
        """
        used to instantiate a selectorParser from a raw string,
        so tokenises the input before returning an instance with the correct tokens
        """
        #bidsschematools already parses some statements? i think...
        #makes this more annoying as you can't just parse everything, you have to check it all...
        if not isinstance(selector, str):
            #do more error checking here idk
            if isinstance(selector, selectorFunc):
                selector.evaluate_static_nodes()
                return selector
            else:
                return selectorFunc(val=selector)

        assert isinstance(selector, str), "from_raw needs a string as input"

        pos = 0
        tokens = [] #tokenised format of input string
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
        

        ret_func = cls(tokens).parse()
        ret_func.evaluate_static_nodes()
        # need to do this on seperate lines, eval_static_nodes returns a boolean of whether it is reduced
        # or not, so it can recursively reduce. We want the object not the boolean
        return ret_func
 
    def __init__(self, tokens:list):
        self.tokens:list = tokens
        self.position:int = 0
        self.total:int = len(tokens)
        self.tags:set = set()

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
        while self.cur_token.kind == 'SEP':
            self.position += 1

    def parse(self) -> selectorFunc:

        if self.position != 0:
            assert self.position == self.total, "SelectorParser did not fully parse selector"
            raise BufferError("Can only parse tokens once")
        
        syntax_tree = self.logic_term()
        if self.position != self.total:
            raise IndexError("Wasn't able to fully parse input expression")

        if "entity" in self.tags:
            raise RuntimeError("INCONSISTENT SCHEMA")
        
        syntax_tree.tags = self.tags #add corresponding tags
        return syntax_tree
    
    LOGIC_OPS = {
        "&&":op_and, # use small functions rather than quick lambda
        "||":op_or,  # so .__name__ returns relevant operation
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

    def number(self):
        val = self.match("NUMBER")
        return selectorFunc(val=int(val))

    def string(self):
        val = self.match("STRING")
        #need to trim outer " " or ' '
        return selectorFunc(val=val[1:-1])

    def parentheses(self):
        self.match("LPAREN")
        node = self.logic_term()
        self.match("RPAREN")
        return node

    def brackets(self):
        assert self.prev_token.kind != "ID", f"parsing logic thinks {self.cur_token} is a list, but context suggests it's an index"
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

    def boolean(self):
        val = self.match("BOOL")
        if val == "true":
            return selectorFunc(val=True)
        elif val == "false":
            return selectorFunc(val=False)

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
    "match":nMatch,
    "max":max,
    "min":min,
    "sorted":sorted,
    "substr":substr,
    "type":nType,
    }

    def identifier(self):
        """
        identifier is a bit special as it adds "tags"

        identifier holds the predefined bids vocabulary of interpreted functions and fields

        Each field and the function "exists()" is considered a tag (these are attributes belonging to a file
        which can be hooked and allow to re-check the schema if these attributes change)
        """
        val = self.match("ID")
        if val in self.FIELDS_MAP.keys():
            self.tags.add(val) #add field to tags
            return selectorFunc(val=self.FIELDS_MAP[val],
                                requires_input=True,
                                is_callable=True)
                
        elif val in self.EVAL_FUNCS.keys():
            self.match("LPAREN")
            args = []

            #can have multiple arguments
            while self.cur_token.val and (self.cur_token.kind != "RPAREN"):
                args.append(self.additive_term())

            self.match("RPAREN")
            if val == "exists":

                self.tags.add(val) #add exists to tag
                return selectorFunc(val=self.EVAL_FUNCS[val],
                                args=args,
                                requires_input=True,
                                is_callable=True)
            
            return selectorFunc(val=self.EVAL_FUNCS[val],
                                args=args,
                                requires_input=False,
                                is_callable=True)
        
        elif val == "null":           
            return selectorFunc(val=None)
        else:
            raise ValueError(f"unrecognised identifier for {val}")

    def primary(self):
        """lowest level priority. These are all considered 
        terminal and just return the interpreted value"""
        cur = self.cur_token
        if cur.kind == "NUMBER":
            return self.number()
        elif cur.kind == "STRING":
            return self.string()
        elif cur.kind == "LPAREN":
            return self.parentheses()
        elif cur.kind == "LBRACK":
            return self.brackets()
        elif cur.kind == "BOOL":
            return self.boolean()
        elif cur.kind == "ID":
            return self.identifier()    
        else:
            raise TypeError(f"Unable to match token {cur}")