from __future__ import absolute_import

import functools
import inspect


class KeyHandler(type):
    @staticmethod
    def key(method):
        @functools.wraps(method)
        def wrapper(cls, *args, **kwargs):
            if hasattr(cls, 'KEY') and cls.KEY:
                return method(cls, cls.KEY, *args, **kwargs)
            else:
                key, args = args[0], args[1:]
                return method(cls, str(key), *args, **kwargs)
        return wrapper

    def __new__(cls, name, bases, attrs):
        for attr, method in ((a, method) for a, method in attrs.iteritems() if not a.startswith('__')):
            if callable(method):
                attrs[attr] = cls.key(method)
            elif inspect.ismethoddescriptor(method):
                attrs[attr] = classmethod(cls.key(method.__func__))
        return super(KeyHandler, cls).__new__(cls, name, bases, attrs)


def decode(cls, value):
    serializer = getattr(cls, 'SERIALIZER', None)
    if value and serializer:
        return serializer.decode.__func__(value)
    else:
        return value


def encode(cls, value):
    serializer = getattr(cls, 'SERIALIZER', None)
    if value and serializer:
        return serializer.encode.__func__(value)
    else:
        return value
