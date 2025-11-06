from bidsbuilder.schema.schema import parse_load_schema
from bidsbuilder.modules.file_bases.tabular_files import _set_tabular_schema, tabularFile
from bidsbuilder.modules.schema_objects import _set_object_schemas
from bidsbuilder.modules.core.dataset_tree import FileCollection

schema = parse_load_schema(debug=True)

_set_object_schemas(schema=schema)
_set_tabular_schema(schema=schema)

test_file = tabularFile()
test_file_name = FileCollection(parent=None, _name=r"C:\Users\augus\BCI_Stuff\Aspen\test.tsv", _file_link=test_file, _name_link=None)
test_file._tree_link = test_file_name

cur_schema = schema.rules.tabular_data.modality_agnostic.Participants
test_file._add_metadata_(cur_schema)
test_file.addRow(pk="sub-person")
test_file.addRow(pk="sub-pers")
test_file.addColumn("age")
test_file.addValues("sub-pers", {"age": 29})
test_file._make_file(force=True)