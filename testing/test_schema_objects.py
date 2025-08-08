from bidsbuilder.modules.schema_objects import *
from bidsbuilder.schema.schema import parse_load_schema


schema = parse_load_schema(debug=True)
_set_object_schemas(schema=schema)


def test_all_have_type_or_definition():
    def check(sub_schema):
        for rule in sub_schema:
            if "type" not in sub_schema[rule] and "definition" not in sub_schema[rule]:
                if instructions := sub_schema[rule].get("anyOf", False):
                    for cur_instr in instructions:
                        if "type" not in cur_instr and "definition" not in cur_instr:
                            print(rule)
                            print(sub_schema[rule])
                            breakpoint()
                else:
                    print(rule)
                    print(sub_schema[rule])
                    breakpoint()

    check(schema.objects.metadata)
    print("done with metadata")
    check(schema.objects.entities)
    print("done with entities")
    check(schema.objects.columns)
    print("done with columns")

test_all_have_type_or_definition()