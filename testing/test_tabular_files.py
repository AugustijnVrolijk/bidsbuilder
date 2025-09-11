from bidsbuilder.schema.schema import parse_load_schema
from bidsbuilder.modules.file_bases.tabular_files import _set_tabular_schema, tabularFile

schema = parse_load_schema(debug=True)

_set_tabular_schema(schema=schema)

test_file = tabularFile()

