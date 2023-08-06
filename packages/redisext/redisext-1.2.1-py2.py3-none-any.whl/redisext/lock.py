from __future__ import absolute_import

import redisext.hashmap
import redisext.key


class Lock(redisext.hashmap.Map, redisext.key.Expire):
    VALUE = ''

    def acquire(self, expiration=None):
        '''
        Acquire a lock.

        :param expiration: lock's expiration time
        :type expiration: int

        :returns: status of lock acquision
        :rtype: bool
        '''
        if self.exists():
            return False
        self.set(self.VALUE)
        if expiration:
            self.expire(expiration)
        return True

    def release(self):
        '''
        Release a lock.

        :returns: status of lock releasion
        :rtype: bool
        '''
        return self.remove()
