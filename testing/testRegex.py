
import re

from wrapBIDS.interpreter import SelectorParser

tester = SelectorParser.from_raw

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

funcs = ["1 + 5 +3", "3*6 && False"]

if __name__ == "__main__":
    for exp in funcs:
        temp = tester(exp)
        final = temp.parse()
        print(final)
        print(final())
    """
    for key, val in strings.items():
        temp = tester(key)
        print(temp.tokens)
        #assert tester == val
    
    for val in funcs:
        tester = _resolve_function(val)
        print(tester)
    """
print("hello")