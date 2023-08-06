from __future__ import absolute_import

import redisext.backend.abc
import redis


class Client(redisext.backend.abc.IClient):
    def __init__(self, host, port, db):
        self._redis = redis.StrictRedis(host, port, db)


class Connection(redisext.backend.abc.IConnection):
    CLIENT = Client
