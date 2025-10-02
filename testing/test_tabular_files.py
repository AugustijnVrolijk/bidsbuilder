from bidsbuilder.schema.schema import parse_load_schema
from bidsbuilder.modules.file_bases.tabular_files import _set_tabular_schema, tabularFile
from bidsbuilder.modules.schema_objects import _set_object_schemas


schema = parse_load_schema(debug=True)

_set_object_schemas(schema=schema)
_set_tabular_schema(schema=schema)

test_file = tabularFile()

cur_schema = schema.rules.tabular_data.modality_agnostic.Participants
test_file._add_metadata_(cur_schema)
print("test")
