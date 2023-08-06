'''
HashMap
-------

.. autoclass:: Map
   :members:

Map could be used for simple and direct key's value manipulations.
For example storing Twitter's username::

   class TwitterUsername(Connection, redisext.hashmap.Map):
       SERIALIZER = redisext.serializer.String

and use-case::

   >>> TwitterUsername(1).put('mylokin')
   True
   >>> TwitterUsername(1).get()
   u'mylokin'

Map also could be used for cache purposes::

   class Cache(Connection, redisext.hashmap.Map):
       SERIALIZER = redisext.serializer.Pickle

use-case example for cache::

   >>> cache = Cache('hash')
   >>> cache.put({'result': 'of', 'cpu intensive': 'calculations'})
   True
   >>> cache.get()
   {'cpu intensive': 'calculations', 'result': 'of'}

.. note::

   Also don't forget to check :class:`redisext.hashmap.HashMap` if you need
   to store more complicated data structures.

'''
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
        ''' Get stored value.

        :returns: stored value
        '''
        value = self.connect_to_slave().get(self.key)
        return self.decode(value)

    def put(self, value):
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
