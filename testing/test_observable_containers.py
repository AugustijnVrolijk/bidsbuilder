#import pytest

from bidsbuilder.util.hooks.new_containers import (
    wrap_container,
    MinimalList,
    MinimalDict,
    MinimalSet,
)


# ----------------------------
# Builtin containers (list, dict, set)
# ----------------------------

def test_builtin_list_instance_upgrade():
    original = [1, 2, 3]
    upgraded = wrap_container(original)
    assert isinstance(upgraded, MinimalList)
    assert upgraded == [1, 2, 3]
    assert upgraded.__class__.__name__.startswith("Observable")

def test_builtin_dict_instance_upgrade():
    original = {"a": 1, "b": 2}
    upgraded = wrap_container(original)
    assert isinstance(upgraded, MinimalDict)
    assert upgraded == {"a": 1, "b": 2}
    assert upgraded.__class__.__name__.startswith("Observable")

def test_builtin_set_instance_upgrade():
    original = {1, 2, 3}
    upgraded = wrap_container(original)
    assert isinstance(upgraded, MinimalSet)
    assert upgraded == {1, 2, 3}
    assert upgraded.__class__.__name__.startswith("Observable")

def test_builtin_type_upgrade():
    obs_list_type = wrap_container(list)
    obs_dict_type = wrap_container(dict)
    obs_set_type = wrap_container(set)

    assert issubclass(obs_list_type, MinimalList)
    assert issubclass(obs_dict_type, MinimalDict)
    assert issubclass(obs_set_type, MinimalSet)
    for tp in (obs_list_type, obs_dict_type, obs_set_type):
        assert tp.__name__.startswith("Observable")


# ----------------------------
# Minimal containers
# ----------------------------

def test_minimal_list_instance_upgrade():
    original = MinimalList([1, 2])
    upgraded = wrap_container(original)
    assert isinstance(upgraded, MinimalList)
    assert upgraded == [1, 2]
    assert upgraded.__class__.__name__.startswith("Observable")

def test_minimal_dict_instance_upgrade():
    original = MinimalDict(a=1)
    upgraded = wrap_container(original)
    assert isinstance(upgraded, MinimalDict)
    assert upgraded == {"a": 1}
    assert upgraded.__class__.__name__.startswith("Observable")

def test_minimal_set_instance_upgrade():
    original = MinimalSet({1, 2})
    upgraded = wrap_container(original)
    assert isinstance(upgraded, MinimalSet)
    assert upgraded == {1, 2}
    assert upgraded.__class__.__name__.startswith("Observable")

def test_minimal_type_upgrade():
    obs_list_type = wrap_container(MinimalList)
    obs_dict_type = wrap_container(MinimalDict)
    obs_set_type = wrap_container(MinimalSet)

    assert issubclass(obs_list_type, MinimalList)
    assert issubclass(obs_dict_type, MinimalDict)
    assert issubclass(obs_set_type, MinimalSet)


# ----------------------------
# User subclasses of minimal types
# ----------------------------

class UserList(MinimalList):
    def extra(self): return "extra!"

class UserDict(MinimalDict):
    def extra(self): return "extra!"

class UserSet(MinimalSet):
    def extra(self): return "extra!"


def test_user_minimal_subclass_instance_upgrade():
    ulist = UserList([10, 20])
    upgraded = wrap_container(ulist)
    assert isinstance(upgraded, UserList)
    assert upgraded == [10, 20]
    assert upgraded.__class__.__name__.startswith("Observable")
    assert upgraded.extra() == "extra!"   # still has user feature

    udict = UserDict({"x": 1})
    upgraded = wrap_container(udict)
    assert isinstance(upgraded, UserDict)
    assert upgraded["x"] == 1
    assert upgraded.__class__.__name__.startswith("Observable")
    assert upgraded.extra() == "extra!"

    uset = UserSet({1, 2})
    upgraded = wrap_container(uset)
    assert isinstance(upgraded, UserSet)
    assert upgraded == {1, 2}
    assert upgraded.__class__.__name__.startswith("Observable")
    assert upgraded.extra() == "extra!"


def test_user_minimal_subclass_type_upgrade():
    obs_user_list = wrap_container(UserList)
    obs_user_dict = wrap_container(UserDict)
    obs_user_set = wrap_container(UserSet)

    assert issubclass(obs_user_list, UserList)
    assert issubclass(obs_user_dict, UserDict)
    assert issubclass(obs_user_set, UserSet)
    for tp in (obs_user_list, obs_user_dict, obs_user_set):
        assert tp.__name__.startswith("Observable")

if __name__ == "__main__":
    test_builtin_dict_instance_upgrade()
    test_builtin_list_instance_upgrade()
    test_builtin_set_instance_upgrade()
    test_builtin_type_upgrade()
    test_minimal_dict_instance_upgrade()
    test_minimal_list_instance_upgrade()
    test_minimal_set_instance_upgrade()
    test_minimal_type_upgrade()
    test_user_minimal_subclass_instance_upgrade()
    test_user_minimal_subclass_type_upgrade()
