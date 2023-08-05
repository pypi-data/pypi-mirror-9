from __future__ import absolute_import

import redisext.models.abc


class HashMap(redisext.models.abc.Model):
    def get(self, hash_key):
        value = self.connect_to_slave().hget(self.key, hash_key)
        return self.decode(value)

    def put(self, hash_key, value):
        value = self.encode(value)
        return self.connect_to_master().hset(self.key, hash_key, value)

    def remove(self, hash_key):
        return bool(self.connect_to_master().hdel(self.key, hash_key))


class Map(redisext.models.abc.Model):
    def get(self):
        value = self.connect_to_slave().get(self.key)
        return self.decode(value)

    def put(self, value):
        value = self.encode(value)
        return self.connect_to_master().set(self.key, value)

    def incr(self, amount=1):
        value = self.connect_to_master().incr(self.key, amount)
        return self.decode(value)

    def decr(self, amount=1):
        value = self.connect_to_master().decr(self.key, amount)
        return self.decode(value)

    def remove(self):
        return bool(self.connect_to_master().delete(self.key))
