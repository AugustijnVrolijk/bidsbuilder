from bidsbuilder.schema.schema import parse_load_schema
from bidsbuilder.schema.interpreter.selectors import selectorHook, SelectorParser

schema = parse_load_schema(debug=True)


def old():
    tests = schema.meta.expression_tests
    passed = 0
    failed = 0
    exception = 0
    #print(tests)
    for i, pair in enumerate(tests):
        expression = pair["expression"]
        result = pair["result"]
        print(f"pair {i}: {pair}")
        print(f"original: {result} of type: {type(result)}")

        func = SelectorParser.from_raw(expression)
        t_result = SelectorParser.from_raw(result)
        try:
            if func() == t_result():
                print("test pass")
                passed += 1
            else:
                print("test failed")
                print(f"intrepreted result:      {func()}")
                print(f"true result:             {t_result}")
                print(f"intrepreted true result: {t_result()}")

                failed += 1
        except Exception as e:
            print("test exception")
            exception += 1

    print(f"passed: {passed}")
    print(f"failed: {failed}")
    print(f"errors: {exception}")


def new():
    tests = schema.meta.expression_tests
    passed = 0
    failed = 0
    exception = 0
    cant_interpret = 0
    #print(tests)
    for i, pair in enumerate(tests):
        expression = pair["expression"]
        result = pair["result"]
        msg = f"\n    pair {i}: {pair}\n    result: {result} of type: {type(result)}"
        try:
            func = SelectorParser.from_raw(expression)
        except Exception:
            print(f"can't interpret{msg}")
            cant_interpret += 1
            continue
    
        try:
            if func() == result:
                #print("test pass")
                passed += 1
            else:
                msg += f"\n    intrepreted result:      {func()}\n    true result:             {result}"
                print(f"test failed{msg}")

                failed += 1
        except Exception as e:
            print(f"test exception{msg}")
            exception += 1

    print(f"\n--------------------------------------------\npassed: {passed}")
    print(f"failed: {failed}")
    print(f"errors: {exception}")
    print(f"can't interpret: {cant_interpret}")

if __name__ == "__main__":
    new()

"""
TESTING NOTES: 

Intersects: 

    schema describes this function as:
        intersects(a: array, b: array) -> array | bool

        The intersection of arrays a and b, or false if there are no shared values.

        intersects(dataset.modalities, ["pet", "mri"])

        Non-empty array if either PET or MRI data is found in dataset, otherwise false
    
    eluding that the return, if it does intersect, would be the array of values found in both.
    BUT tests show:
        - expression: intersects([1], [1, 2])
        result: true
    which gives a test failed as I return [1] or the intersection between these lists..

NULL:
    the readthedocs: https://bidsschematools.readthedocs.io/en/latest/description.html#the-special-value-null
    say that null propogates through everything: 

    i.e. that: null && true == null
               null || true == null   

    but the schema shows this the other way around:
    {'expression': 'false && null', 'result': False}
    {'expression': 'true || null', 'result': True}

    apart from: 
    {'expression': 'false || null', 'result': None} 

    which way should it be...

    there are similar cases with 
    {'expression': 'allequal(null, [])', 'result': False}
    {'expression': "match(null, 'pattern')", 'result': None}
    {'expression': "match('string', null)", 'result': False}
"""


"""
ADD TESTS:
using schema.meta.context i can assert that the fields have all the required values.
    Make all possible combos ()

"""