import re
from wrapBIDS.Modules.selectors import SelectorParser

def _smart_split(s):
    # Step 1: Use regex to capture meaningful tokens
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


strings= [
    'exists(sidecar.IntendedFor, "subject")',
    'count(columns.type, "EEG")',
    'intersects(dataset.modalities, ["pet", "mri"])',
    'length(columns.onset) > 0',
    'sorted(sidecar.VolumeTiming) == sidecar.VolumeTiming',
    'entities.task != "rest"',
    '"Units" in sidecar && sidecar.Units == "mm"'
    '!exists(sidecar.IntendedFor, "subject")',
    '!exists(sidecar.IntendedFor, "subject") != False',
]

testerino = SelectorParser()
for string in strings:
    tester = testerino.parseSelector(string)
print("hello")