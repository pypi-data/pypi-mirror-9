from __future__ import absolute_import


class Expire(object):
    EXPIRE = None

    def expire(self, seconds=None):
        if seconds is None:
            try:
                seconds = int(self.EXPIRE)
            except TypeError:
                raise ValueError(seconds)
        return self.connect_to_master().expire(self.key, seconds)

    def ttl(self):
        return self.connect_to_master().ttl(self.key)

    def persist(self):
        return self.connect_to_master().persist(self.key)
