from __future__ import absolute_import

import redisext.utils


class HashMap(object):
    __metaclass__ = redisext.utils.KeyHandler
    KEY = None

    @classmethod
    def get(cls, key, hash_key):
        value = cls.connect_to_slave().hget(key, hash_key)
        return redisext.utils.decode(cls, value)

    @classmethod
    def put(cls, key, hash_key, value):
        value = redisext.utils.encode(cls, value)
        return cls.connect_to_master().hset(key, hash_key, value)

    @classmethod
    def remove(cls, key, hash_key):
        return bool(cls.connect_to_master().hdel(key, hash_key))


class Map(object):
    __metaclass__ = redisext.utils.KeyHandler

    @classmethod
    def get(cls, key):
        value = cls.connect_to_slave().get(key)
        return redisext.utils.decode(cls, value)

    @classmethod
    def put(cls, key, value):
        value = redisext.utils.encode(cls, value)
        return cls.connect_to_master().set(key, value)

    @classmethod
    def incr(cls, key, amount=1):
        value = cls.connect_to_master().incr(key, amount)
        return redisext.utils.decode(cls, value)

    @classmethod
    def decr(cls, key, amount=1):
        value = cls.connect_to_master().decr(key, amount)
        return redisext.utils.decode(cls, value)

    @classmethod
    def remove(cls, key):
        return bool(cls.connect_to_master().delete(key))
