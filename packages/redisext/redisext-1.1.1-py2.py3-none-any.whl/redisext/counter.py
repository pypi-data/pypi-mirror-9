from __future__ import absolute_import

import redisext.models.abc


class Counter(redisext.models.abc.Model):
    def increment(self):
        value = self.connect_to_master().incr(self.key)
        return self.decode(value)

    def get(self):
        value = self.connect_to_slave().get(self.key)
        return self.decode(value)
