from bidsbuilder.schema.schema import parse_load_schema
from bidsbuilder.schema.interpreter.selectors import selectorHook, SelectorParser

schema = parse_load_schema(debug=True)

tests = schema.meta.expression_tests
passed = 0
failed = 0
exception = 0
#print(tests)
for i, pair in enumerate(tests):
    expression = pair["expression"]
    result = pair["result"]
    print(f"pair {i}: {pair}")

    func = SelectorParser.from_raw(expression)
    t_result = SelectorParser.from_raw(result)
    try:
        if func() == t_result():
            print("test pass")
            passed += 1
        else:
            print("test failed")
            print(f"intrepreted result: {func}")
            print(f"true result:        {t_result}")
            failed += 1
    except Exception as e:
        print("test exception")
        exception += 1

print(f"passed: {passed}")
print(f"failed: {failed}")
print(f"errors: {exception}")


"""
ADD TESTS:
using schema.meta.context i can assert that the fields have all the required values.
    Make all possible combos ()

"""