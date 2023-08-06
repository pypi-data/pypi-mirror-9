from __future__ import absolute_import

import redisext.models.abc


class Queue(redisext.models.abc.Model):
    def pop(self):
        '''
        Pop item from queue.

        :returns: item from queue
        '''
        item = self.connect_to_master().rpop(self.key)
        return self.decode(item)

    def push(self, item):
        '''
        Push item into queue.

        :param item:
        :type item:

        :returns: number of items in queue
        :rtype: int
        '''
        item = self.encode(item)
        return self.connect_to_master().lpush(self.key, item)


class PriorityQueue(redisext.models.abc.Model):
    def pop(self):
        redis = self.connect_to_master()
        item = redis.zrangebyscore(self.key, '-inf', '+inf', num=1)
        item = item[0] if item else None
        redis.zrem(self.key, item)
        return self.decode(item)

    def push(self, item, priority):
        item = self.encode(item)
        return self.connect_to_master().zadd(self.key, int(priority), item)
