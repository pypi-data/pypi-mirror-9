from __future__ import absolute_import

import json
import pickle


class JSON(object):
    @staticmethod
    def encode(item):
        return json.dumps(item)

    @staticmethod
    def decode(item):
        if isinstance(item, bytes):
            item = item.decode()
        return json.loads(item)


class String(object):
    @staticmethod
    def encode(item):
        return str(item)

    @staticmethod
    def decode(item):
        if isinstance(item, bytes):
            item = item.decode()
        return item


class Numeric(object):
    @staticmethod
    def encode(item):
        return int(item)

    @staticmethod
    def decode(item):
        return int(item)


class Pickle(object):
    @staticmethod
    def encode(item):
        return pickle.dumps(item)

    @staticmethod
    def decode(item):
        return pickle.loads(item)
