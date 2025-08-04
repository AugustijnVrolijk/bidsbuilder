from unittest.mock import Mock

from bidsbuilder.modules.core.dataset_tree import Directory
from bidsbuilder.modules.core.filenames import CompositeFilename, _set_filenames_schema
from bidsbuilder.schema.schema import parse_load_schema
from bidsbuilder.modules.schema_objects import _set_object_schemas

schema = parse_load_schema()
_set_filenames_schema(schema)
_set_object_schemas(schema)

mock_function = Mock()

def _update_children_cback_new(instance:'CompositeFilename', *args, **kwargs):
    """
    Callback method which calls on self and all child instances to check their schema 
    add tags to specify which selectors to re-check
    """
    instance._tree_link.name = instance.local_name
    for i, child in enumerate(instance._tree_link._iter_tree()):
        mock_function(i, child._name_link.local_name)
    return

CompositeFilename.entities.callback = _update_children_cback_new
CompositeFilename.datatype.callback = _update_children_cback_new
CompositeFilename.suffix.callback = _update_children_cback_new

base_Name = CompositeFilename.create(entities={"subject":"base1"}, suffix="eeg")
base = Directory(_name=None, _file_link=None, _name_link=base_Name, parent=None)

ses1 = CompositeFilename.create(entities={"session":"yay1"})
base.add_child(ses1, None, 'Directory')

ses2 = CompositeFilename.create(entities={"session":"yay2"})
base.add_child(ses2, None, 'Directory')

def test_name_inheritance():
    assert ses2.name == "sub-base1_ses-yay2_eeg"
    assert ses1.local_name == "ses-yay1"
    p1 = id(ses1.parent)
    p2 = id(base._name_link)
    assert p1 == p2

def test_change_info_callback():
    base_Name.suffix = "anat"
    assert ses2.name == "sub-base1_ses-yay2_anat"

    assertion_calls = [(0,"ses-yay1"),(1,"ses-yay2")]
    assert mock_function.assert_has_calls(assertion_calls)

def test_change_info_tree_ref():
    ses2.entities["session"] = "new1"
    assert "ses-new1" in base.children.keys()

if __name__ == "__main__":
    test_name_inheritance()
    test_change_info_callback()
    test_change_info_tree_ref()

