
import re

from wrapBIDS.interpreter import SelectorParser
from typing import Tuple, Union
from collections.abc import Callable
from functools import wraps

tester = SelectorParser.from_raw

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


strings = {
    'exists(sidecar.IntendedFor", "subject")':['exists(sidecar.IntendedFor "subject")'],
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
        print(temp.tokens)
        #assert tester == val
    """
    for val in funcs:
        tester = _resolve_function(val)
        print(tester)
    """
print("hello")