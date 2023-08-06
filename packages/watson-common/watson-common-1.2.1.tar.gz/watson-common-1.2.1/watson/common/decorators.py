# -*- coding: utf-8 -*-
class cached_property(object):

    """Allows expensive property calls to be cached.

    Once the property is called, it's result is stored in the corresponding
    property name prefixed with an underscore.

    Example:

    .. code-block:: python

        class MyClass(object):
            @cached_property
            def expensive_call(self):
                # do something expensive

        klass = MyClass()
        klass.expensive_call  # initial call is made
        klass.expensive_call  # return value is retrieved from an internal cache
        del klass._expensive_call
    """

    def __init__(self, func):
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self.key = '_{name}'.format(name=self.__name__)
        self.func = func

    def __get__(self, obj, type=None):
        if self.key not in obj.__dict__:
            obj.__dict__[self.key] = self.func(obj)
        return obj.__dict__[self.key]
