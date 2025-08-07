from functools import wraps

from types import MethodType
from functools import wraps


"""

possibly used in the future to dynamically create observable containers

i.e. for list /dict, set or even custom types..

May be useful to create both validator and non validator observable types


"""

def make_observable_type(base_cls, mutating_methods=None):
    """
    Dynamically creates a subclass of `base_cls` that triggers a callback and applies a validator.
    """
    if mutating_methods is None:
        mutating_methods = {
            'list': ['__setitem__', 'append', 'extend', 'insert', '__delitem__'],
            'dict': ['__setitem__', 'update', '__delitem__', 'pop', 'popitem', 'setdefault']
        }[base_cls.__name__]  # choose based on base class

    class Observable(base_cls):
        def __init__(self, *args, callback=None, validator=None, **kwargs):
            super().__init__(*args, **kwargs)
            self._callback = callback or (lambda: None)
            self._validator = validator or (lambda x: x)
            self._frozen = False

        def _check_callback(self):
            if not self._frozen:
                self._callback()

    # Wrap mutating methods
    for method_name in mutating_methods:
        original = getattr(base_cls, method_name, None)
        if original is None:
            continue

        @wraps(original)
        def wrapper(self, *args, _original=original, **kwargs):
            # Apply validator where applicable
            if method_name == '__setitem__':
                args = (args[0], self._validator(args[1]))
            elif method_name in ('append', 'insert'):
                args = (self._validator(args[0]),)
            elif method_name == 'extend':
                args = ([self._validator(x) for x in args[0]],)
            elif method_name == 'update':
                if args:
                    args = ({k: self._validator(v) for k, v in args[0].items()},)
                elif kwargs:
                    kwargs = {k: self._validator(v) for k, v in kwargs.items()}

            result = _original(self, *args, **kwargs)
            self._check_callback()
            return result

        setattr(Observable, method_name, wrapper)

    return Observable

class ObservableMeta(type):
    def __new__(mcs, name, bases, namespace, mutating_methods=None):
        cls = super().__new__(mcs, name, bases, namespace)

        if mutating_methods is None:
            # Default mutating methods for common container types
            mutating_methods = {
                '__setitem__', '__delitem__', 'append', 'extend',
                'insert', 'remove', 'pop', 'clear', 'update', 'setdefault'
            }

        for attr_name in mutating_methods:
            orig_method = getattr(cls, attr_name, None)
            if not orig_method:
                continue

            @wraps(orig_method)
            def wrapper(self, *args, _original=orig_method, _name=attr_name, **kwargs):
                # Optional validator logic
                args = self._validate_args(_name, args, kwargs)
                result = _original(self, *args, **kwargs)
                self._check_callback()
                return result

            setattr(cls, attr_name, wrapper)

        return cls

class Observable(metaclass=ObservableMeta):
    def __init__(self, *args, callback=None, validator=None, **kwargs):
        self._callback = callback or (lambda: None)
        self._validator = validator or (lambda x: x)
        self._frozen = False

    def _check_callback(self):
        if not self._frozen:
            self._callback()

    def _validate_args(self, method, args, kwargs):
        if method in {'append', 'insert'}:
            return (self._validator(args[0]),), kwargs
        elif method == '__setitem__':
            return (args[0], self._validator(args[1])), kwargs
        elif method == 'extend':
            return ([self._validator(x) for x in args[0]],), kwargs
        elif method == 'update':
            if args:
                args = ({k: self._validator(v) for k, v in args[0].items()},)
            elif kwargs:
                kwargs = {k: self._validator(v) for k, v in kwargs.items()}
            return args, kwargs
        return args, kwargs
