class Dataset:
    def __init__(self):
        self.tree = {}  # maps file paths to object references

    def register_object(self, path: str, obj: object):
        """Registers an object at a specific path in the tree."""
        norm_path = path.lstrip("/")  # normalize
        self.tree[norm_path] = obj

    def get_by_path(self, path: str):
        norm_path = path.lstrip("/")
        return self.tree.get(norm_path, None)


class TreeNode:
    def __init__(self):
        self.children = {}
        self.object = None  # link to dataset object

    def add(self, path: str, obj: object):
        parts = path.strip("/").split("/")
        node = self
        for part in parts:
            node = node.children.setdefault(part, TreeNode())
        node.object = obj

    def get(self, path: str):
        parts = path.strip("/").split("/")
        node = self
        for part in parts:
            node = node.children.get(part)
            if node is None:
                return None
        return node.object
