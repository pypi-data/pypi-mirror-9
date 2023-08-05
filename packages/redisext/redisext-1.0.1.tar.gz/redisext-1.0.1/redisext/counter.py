from __future__ import absolute_import

import redisext.utils


class Counter(object):
    __metaclass__ = redisext.utils.KeyHandler
    KEY = None

    @classmethod
    def increment(cls, key):
        value = cls.connect_to_master().incr(key)
        return redisext.utils.decode(cls, value)

    @classmethod
    def get(cls, key):
        value = cls.connect_to_slave().get(key)
        return redisext.utils.decode(cls, value)
