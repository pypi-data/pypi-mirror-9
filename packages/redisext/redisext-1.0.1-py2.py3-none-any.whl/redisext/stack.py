from __future__ import absolute_import

import redisext.serializer
import redisext.utils


class Stack(object):
    __metaclass__ = redisext.utils.KeyHandler
    KEY = None

    @classmethod
    def pop(cls, key):
        item = cls.connect_to_master().lpop(key)
        return redisext.utils.decode(cls, item)

    @classmethod
    def push(cls, key, item):
        item = redisext.utils.encode(cls, item)
        return cls.connect_to_master().lpush(key, item)
