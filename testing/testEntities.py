from bidsbuilder.util.schema import parse_load_schema

schema = parse_load_schema(debug=True)

from bidsbuilder.modules.filenames import CompositeFilename
from bidsbuilder.modules.schema_objects import *

_set_object_schemas(schema)

a = Entity("SUB", "1")
print(a)
print(a.display_name)
print(a.description)
a.val = "123"
print(a)
print(a.str_name)


b = Suffix("tb1SrgE")
print(b)
c = Entity("task", "reading")


d = CompositeFilename(None, {a.name:a}, b)
print(d)
print(d.name)

a.val="numberOne"
print(d.name)

e = CompositeFilename(d, {c.name:c})
print(e.name)

print(e)
print(e.suffix)