from __future__ import absolute_import

import redisext.models.abc


class Stack(redisext.models.abc.Model):
    def pop(self):
        '''
        Pop item from stack.
        '''
        item = self.connect_to_master().lpop(self.key)
        return self.decode(item)

    def push(self, item):
        '''
        Push item into queue.

        :returns: number of items in queue
        :rtype: int
        '''
        item = self.encode(item)
        return self.connect_to_master().lpush(self.key, item)
