from __future__ import absolute_import

import redisext.models.abc


class Pool(redisext.models.abc.Model):
    def pop(self):
        item = self.connect_to_master().spop(self.key)
        return self.decode(item)

    def push(self, item):
        item = self.encode(item)
        return self.connect_to_master().sadd(self.key, item)


class SortedSet(redisext.models.abc.Model):
    def add(self, element, score):
        element = self.encode(element)
        return bool(self.connect_to_master().zadd(self.key, score, element))

    def length(self, start_score, end_score):
        return int(self.connect_to_slave().zcount(self.key, start_score, end_score))

    def members(self):
        elements = self.connect_to_slave().zrevrange(self.key, 0, -1)
        if not elements:
            return elements

        return [self.decode(e) for e in elements]

    def contains(self, element):
        element = self.encode(element)
        return self.connect_to_slave().zscore(self.key, element) is not None

    def truncate(self, size):
        return int(self.connect_to_master().zremrangebyrank(self.key, 0, -1 * size - 1))

    def clean(self):
        return bool(self.connect_to_master().delete(self.key))
