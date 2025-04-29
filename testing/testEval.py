class simpleClass():
    def __init__(self, a, b):
        self.a = a
        self.b = b
        pass

def isNone(val):
    print(val)
    if val is None:
        return True
    else:
        return False

root2 = simpleClass(5, None)

def parseEval(test):
    a = f"isNone(root.a)"
    b = f"isNone(root.b)"

    isA = eval(a, globals={"isNone":isNone}, locals={"root":test})

    print(f"{a}{isA}")
    print(f"{b}{eval(b, globals={"isNone":isNone}, locals={"root":test})}")

parseEval(root2)