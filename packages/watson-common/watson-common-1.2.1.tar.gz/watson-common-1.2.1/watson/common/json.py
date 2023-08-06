# -*- coding: utf-8 -*-
from watson.common import strings


def serialize(obj, attributes, strategies=None, camelcase=True, **kwargs):
    """Serializes an object into a dict suitable to be dumped to json.

    Args:
        obj (mixed): The object to serialize
        attributes (tuple): A tuple of attributes that should be serialized
        strategies (dict): Key/value pairs of strategies to deal with objects
        camelcase (bool): camelCase the attribute names
        kwargs: Passed to the strategy when it's called

    Example:

    .. code-block:: python

        class AnotherClass(object):
            name = 'Else'

        class MyClass(object):
            name = 'Something'
            complex_classes = [AnotherClass()]

        class_ = MyClass()
        d = serialize(class_, ('name', 'complex'),
                       strategies={
                            'complex_class': lambda x:
                                                serialize(y, ('name',))
                                                for y in x})
        # {'name': 'Something', 'complexClass': {'name': 'Else'}}
    """
    serialized = {}
    for attr in attributes:
        value = getattr(obj, attr)
        if value is None:
            continue
        if strategies and attr in strategies:
            value = strategies[attr](value, **kwargs)
        if camelcase:
            attr = strings.camelcase(attr, uppercase=False)
        serialized[attr] = value
    return serialized


def deserialize(obj, class_, attributes, strategies=None, snakecase=True,
                **kwargs):
    """Deserializes a dict into an object of type class_.

    Can be seen as the inverse of serialize().

    Args:
        obj (dict): The structure to deserialize
        class_ (class): The type that the object should be deserialized into
        attributes (tuple): A tuple of attributes that should be set
        strategies (dict): Key/value pairs of strategies to deal with objects
        snakecase (bool): snake_case the attribute names
        kwargs: Passed to the strategy when it's called
    """
    deserialized = class_()
    for attr in attributes:
        if snakecase:
            # camelcase the required attr
            attr = strings.camelcase(attr, uppercase=False)
        value = obj.get(attr)
        if value is None:
            continue
        if strategies and attr in strategies:
            value = strategies[attr](value, **kwargs)
        if snakecase:
            attr = strings.snakecase(attr)
        setattr(deserialized, attr, value)
    return deserialized
