from .equals_builder import EqualsBuilder
from .hash_code_builder import HashCodeBuilder


__all__ = [
    'hashable',
    'equalable',
]


def hashable(cls=None, attributes=None, methods=None):
    _validate_attributes_and_methods(attributes, methods)

    def decorator(cls):
        cls = equalable(cls, attributes, methods)
        cls.__hash__ = HashCodeBuilder.auto_generate(cls, attributes, methods)
        return cls
    return decorator if cls is None else decorator(cls)


def equalable(cls=None, attributes=None, methods=None):
    _validate_attributes_and_methods(attributes, methods)

    def decorator(cls):
        cls.__eq__ = EqualsBuilder.auto_generate(cls, attributes, methods)
        cls.__ne__ = EqualsBuilder.auto_ne_from_eq()
        return cls
    return decorator if cls is None else decorator(cls)


def _validate_attributes_and_methods(attributes, methods):
    assert not isinstance(attributes, basestring), 'attributes must be list'
    assert not isinstance(methods, basestring), 'methods must be list'

    assert attributes or methods, 'attributes or methods must be NOT empty'
