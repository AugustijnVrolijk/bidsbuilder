from wrapBIDS.interpreter import SelectorParser

def _smart_split(s:str) -> list[str]:
    #split based on whitespace
    tokens = s.split()

    #need to merge function calls, list comprehensions and seperate not: "!"
    final_tokens = []
    tokenLen = len(tokens)
    i = 0
    while i < tokenLen:
        cur = tokens[i]

        #check if I need to merge function
        if cur.count("(") != cur.count(")"):
            cur, new_i = _complete_token(tokens[i:], ["(",")"])
            i += new_i
            
        #check if I need to merge list
        elif cur.count("[") != cur.count("]"):
            cur, new_i = _complete_token(tokens[i:], ["[","]"])
            i += new_i

        #seperate not
        if cur[0] == '!' and cur[1] != "=":
            final_tokens.append(cur[0])
            cur = cur[1:]

        final_tokens.append(cur)
        i += 1

    return final_tokens

def _complete_token(tokens:list[str], checkval:tuple[str, str]) -> tuple[str, int]:
    
    cur:str = ""
    for i in range(len(tokens)):
        cur += f" {tokens[i]}"
        if cur.count(checkval[0]) == cur.count(checkval[1]):
            return cur.strip(), i
    
    raise IndexError("couldn't complete sequence")

def _assign_token(tokens:list[str]):
    return

def _split_function(s:str) -> tuple[str, list[str]]:
    assert s[-1] == ")"

    function:str
    arguments:list

    
    for i in range(len(s)):
        if s[i] == "(":
            function = s[:i]
            arguments = s[(i+1):]
            break
    
    return

strings= {
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

if __name__ == "__main__":

    for key, val in strings.items():
        tester = _smart_split(key)
        assert tester == val

print("hello")