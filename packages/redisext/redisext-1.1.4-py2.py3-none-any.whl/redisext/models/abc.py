from __future__ import absolute_import


class Model(object):
    KEY = None

    def __init__(self, key=None):
        self.key = key or getattr(self, 'KEY', None)

    @classmethod
    def decode(cls, value):
        serializer = getattr(cls, 'SERIALIZER', None)
        if value and serializer:
            return serializer.decode(value)
        else:
            return value

    @classmethod
    def encode(cls, value):
        serializer = getattr(cls, 'SERIALIZER', None)
        if value and serializer:
            return serializer.encode(value)
        else:
            return value
