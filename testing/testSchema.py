from bidsbuilder.util.schema import parse_load_schema
from bidsbuilder.interpreter.selectors import selectorHook
schema = parse_load_schema(debug=True)

tests = schema.meta.expression_tests

#print(tests)
for i, pair in enumerate(tests):
    expression = pair["expression"]
    result = pair["result"]
    print(type(result))
    print(f"pair: {pair}")
    #print(f"expresson: {expression}")
    #print(f"result: {result}")

    test = selectorHook.from_raw(expression)
    #tRes = selectorHook.from_raw(result)
    print(f"\n{test}")
    try:
        res = test()
        print(res)
    except Exception as e:
        print(e)
    breakpoint()

