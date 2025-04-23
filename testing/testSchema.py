import bidsschematools as bst
import bidsschematools.schema
import bidsschematools.types
import bidsschematools.utils

bidsschematools.schema.filter_schema

schema = bidsschematools.schema.load_schema()
keys = schema.keys()
for key in keys:
    print(key)

def printKeys(schema):
    if not isinstance(schema, bidsschematools.types.namespace.Namespace):
        print(schema)
        raw_keys = schema
    else:
        keys = schema.keys()
        raw_keys = []
        for key in keys:
            print(key)
            raw_keys.append(key)
    return raw_keys

print("hello")