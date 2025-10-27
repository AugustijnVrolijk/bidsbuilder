from bidsbuilder.schema.schema import parse_load_schema
from bidsbuilder.modules.file_bases.tabular_files import _set_tabular_schema, tabularFile
from bidsbuilder.modules.schema_objects import _set_object_schemas


schema = parse_load_schema(debug=True)

_set_object_schemas(schema=schema)
_set_tabular_schema(schema=schema)

test_file = tabularFile()

cur_schema = schema.rules.tabular_data.modality_agnostic.Participants
test_file._add_metadata_(cur_schema)
cur_data = test_file.data
cur_data.addColumn("age")
cur_data.data.loc[1] = 15
cur_data.data.loc[2] = 18
cur_data.data.loc[3] = 11
cur_data.data.to_csv(r"C:\Users\augus\BCI_Stuff\Aspen\test.csv")
print("test")

