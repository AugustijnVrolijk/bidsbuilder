
import re

from wrapBIDS.interpreter import SelectorParser
from typing import Tuple, Union
from collections.abc import Callable
from functools import wraps


_smart_split = SelectorParser._smart_split
_complete_token = SelectorParser._complete_token

tester = SelectorParser._parse_tokens

def feedListToStr(func):
    """
    ensures no clashes between path stem and entities, also converts path into stem and entities for easier downstream parsing
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

@feedListToStr
def _resolve_field(s:str) -> Union[Tuple[Callable, str], Callable,str]:
    #case 1: string is a unknown string, defined by ""
    s = s.strip()
    
    if s.startswith(('"', "'")) and s.endswith(('"', "'")):
        return s[1:-1]

    #case 2: string has a .
    if "." in s:
        tokens = s.split(".")
        assert len(tokens) == 2
        return (tokens[0].strip(), tokens[1].strip())
    
    #case 3: string has a []
    if ("[" in s) and ("]" in s):
        assert s.startswith('[') and s.endswith(']')
        s = s[1:-1]
        tokens = re.split(r"[ ,]", s)
        return _resolve_field(tokens)
    
    #final case, its just in the field map
    return "hehehe"

def _resolve_function(s:str) -> Tuple[str, list[str]]:
    assert s.endswith(")")
    s = s[:-1]

    function:str
    raw_arguments:str
    for i in range(len(s)):
        if s[i] == "(":
            function = s[:i]
            raw_arguments = s[(i+1):]
            break
    
    token_arguments = _smart_split(raw_arguments, ",")
    final_arguments:list = []
    for token in token_arguments:
        final_arguments.append(_resolve_field(token))

    return (function, final_arguments)

strings = {
    'exists(sidecar.IntendedFor, "subject")':['exists(sidecar.IntendedFor "subject")'],
    'count(columns.type, "EEG")':['count(columns.type "EEG")'],
    'intersects(dataset.modalities, ["pet", "mri"])':['intersects(dataset.modalities ["pet" "mri"])'],
    'length(columns.onset) > 0':['length(columns.onset)', '>', '0'],
    'sorted(sidecar.VolumeTiming) == sidecar.VolumeTiming':['sorted(sidecar.VolumeTiming)', '==', 'sidecar.VolumeTiming'],
    'entities.task != "rest"':['entities.task', '!=', '"rest"'],
    '"Units" in sidecar && sidecar.Units == "mm"':['"Units"', 'in', 'sidecar', '&&', 'sidecar.Units', '==', '"mm"'],
    '!exists(sidecar.IntendedFor, "subject")':['!', 'exists(sidecar.IntendedFor "subject")'],
    '!exists(sidecar.IntendedFor, "subject") != False':['!', 'exists(sidecar.IntendedFor "subject")', '!=', 'False'],
    'index(["i", "j", "k"], axis)':['index(["i" "j" "k"] axis)'],
}

strings2= {
    'exists(sidecar.IntendedFor, "subject")':['exists(sidecar.IntendedFor, "subject")'],
    'count(columns.type, "EEG")':['count(columns.type, "EEG")'],
    'intersects(dataset.modalities, ["pet", "mri"])':['intersects(dataset.modalities, ["pet", "mri"])'],
    'length(columns.onset) > 0':['length(columns.onset)', '>', '0'],
    'sorted(sidecar.VolumeTiming) == sidecar.VolumeTiming':['sorted(sidecar.VolumeTiming)', '==', 'sidecar.VolumeTiming'],
    'entities.task != "rest"':['entities.task', '!=', '"rest"'],
    '"Units" in sidecar && sidecar.Units == "mm"':['"Units"', 'in', 'sidecar', '&&', 'sidecar.Units', '==', '"mm"'],
    '!exists(sidecar.IntendedFor, "subject")':['!', 'exists(sidecar.IntendedFor, "subject")'],
    '!exists(sidecar.IntendedFor, "subject") != False':['!', 'exists(sidecar.IntendedFor, "subject")', '!=', 'False'],
    'index(["i", "j", "k"], axis)':['index(["i", "j", "k"], axis)'],
}

funcs = ['!exists(sidecar.IntendedFor, "subject")',
         'index(["i", "j", "k"], axis)']

if __name__ == "__main__":
    
    for key, val in strings.items():
        temp = tester(key)
        print(temp)
        #assert tester == val
    """
    for val in funcs:
        tester = _resolve_function(val)
        print(tester)
    """
print("hello")