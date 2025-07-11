from bidsbuilder.util.schema import parse_load_schema

schema = parse_load_schema(debug=True)

from bidsbuilder.modules.entities import *
Entity.schema = schema.objects.entities
Column.schema = schema.objects.columns
Suffix.schema = schema.objects.suffixes
Metadata.schema = schema.objects.metadata
CompositeFilename.schema = schema.rules.entities

a = Entity("Subject", "1")
print(a)
print(a.display_name)
print(a.description)
a.val = "subject<1>"
print(a)