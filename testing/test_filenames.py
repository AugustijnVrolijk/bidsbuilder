from bidsbuilder.modules.core.dataset_tree import Directory
from bidsbuilder.modules.core.filenames import CompositeFilename


def _update_children_cback_new(instance:'CompositeFilename'):
    """
    Callback method which calls on self and all child instances to check their schema 
    add tags to specify which selectors to re-check
    """
    for i, child in enumerate(instance._tree_link._iter_tree()):
        print(f"child {i}: {child}")
    return

CompositeFilename.entities.callback = _update_children_cback_new
CompositeFilename.datatype.callback = _update_children_cback_new
CompositeFilename.suffix.callback = _update_children_cback_new

print("hello")

base_Name = CompositeFilename({"subject":"base1"})
base = Directory(_name=None, _file_link=base_Name, _name_link=None, parent=None)

ses1 = CompositeFilename({"entities":"yay1"})
base.add_child()

ses1_dir = Directory(_name=None, _file_link=base_Name, _name_link=None, parent=base)

base_Name = CompositeFilename({"subject":"base1"})
base = Directory(_name=None, _file_link=base_Name, _name_link=None, parent=None)
