from __future__ import absolute_import

import redisext.models.abc


class HashMap(redisext.models.abc.Model):
    def get(self, hash_key):
        value = self.connect_to_slave().hget(self.key, hash_key)
        return self.decode(value)

    def set(self, hash_key, value):
        value = self.encode(value)
        return self.connect_to_master().hset(self.key, hash_key, value)

    def remove(self, hash_key):
        return bool(self.connect_to_master().hdel(self.key, hash_key))


class Map(redisext.models.abc.Model):
    def get(self):
        ''' Get stored value.

        :returns: stored value
        '''
        value = self.connect_to_slave().get(self.key)
        return self.decode(value)

    def set(self, value):
        ''' Store value into map.

        :param value:
        :type value:

        :returns: status if value saved or not
        :rtype: bool
        '''
        value = self.encode(value)
        return self.connect_to_master().set(self.key, value)

    def incr(self, value=1):
        ''' Increase stored value.

        :param value: value to add
        :type value: int

        :returns: current value
        '''
        value = self.connect_to_master().incr(self.key, value)
        return self.decode(value)

    def decr(self, value=1):
        ''' Decrease stored value.

        :param value: value to add
        :type value: int

        :returns: current value
        '''
        value = self.connect_to_master().decr(self.key, value)
        return self.decode(value)

    def remove(self):
        ''' Remove value from map.

        :returns: status of removal
        :rtype: bool
        '''
        return bool(self.connect_to_master().delete(self.key))

    def exists(self):
        ''' Returns status if key exists or not

        :returns: existence
        :rtype: bool
        '''
        return bool(self.connect_to_master().exists(self.key))
