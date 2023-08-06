'''
Counter
-------

.. autoclass:: Counter
   :members:

Example of unread messages counter::

   class Unread(Connection, redisext.counter.Counter):
       SERIALIZER = redisext.serializer.Numeric

could be used like::

   >>> unread = Unread('messages')
   >>> unread.get()  # key does not exist
   >>> unread.incr()
   1
   >>> unread.incr(5)
   6
   >>> unread.get()
   6
'''
from __future__ import absolute_import

import redisext.models.abc


class Counter(redisext.models.abc.Model):
    def get(self):
        ''' Get counter's value.

        :returns: counter's value
        :rtype: int
        '''
        value = self.connect_to_slave().get(self.key)
        return self.decode(value)

    def incr(self, value=1):
        ''' Increment counter by `value`.

        :param value: value to add
        :type value: int

        :returns: counter's value
        :rtype: int
        '''
        value = self.connect_to_master().incr(self.key, value)
        return self.decode(value)
