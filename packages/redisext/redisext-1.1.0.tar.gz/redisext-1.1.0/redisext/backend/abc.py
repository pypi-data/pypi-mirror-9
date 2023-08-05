class IClient(object):
    ''' Interface for redis client '''

    def __init__(self, **kwargs):
        raise NotImplementedError()

    def expire(self, key, seconds):
        return self._redis.expire(key, seconds)

    def flushdb(self):
        return self._redis.flushdb()

    def delete(self, key):
        return self._redis.delete(key)

    def get(self, key):
        return self._redis.get(key)

    def hdel(self, key, hash_key):
        return self._redis.hdel(key, hash_key)

    def hget(self, key, hash_key):
        return self._redis.hget(key, hash_key)

    def hset(self, key, hash_key, value):
        return self._redis.hset(key, hash_key, value)

    def lpop(self, key):
        return self._redis.lpop(key)

    def lpush(self, key, item):
        return self._redis.lpush(key, item)

    def persist(self, key):
        return self._redis.persist(key)

    def rpop(self, key):
        return self._redis.rpop(key)

    def sadd(self, key, item):
        return self._redis.sadd(key, item)

    def set(self, key, value):
        return self._redis.set(key, value)

    def spop(self, key):
        return self._redis.spop(key)

    def ttl(self, key):
        return self._redis.ttl(key)

    def zadd(self, key, *args, **kwargs):
        return self._redis.zadd(key, *args, **kwargs)

    def incr(self, key, amount=1):
        return self._redis.incr(key, amount)

    def decr(self, key, amount=1):
        return self._redis.decr(key, amount)

    def zrangebyscore(self, key, min_score, max_score, start=0, num=1):
        return self._redis.zrangebyscore(
            key,
            min_score,
            max_score,
            start=start,
            num=num,
        )

    def zrem(self, key, item):
        return self._redis.zrem(key, item)

    def zcount(self, key, start_score, end_score):
        return self._redis.zcount(key, start_score, end_score)

    def zremrangebyrank(self, key, start, stop):
        return self._redis.zremrangebyrank(key, start, stop)

    def zrevrange(self, key, start, stop):
        return self._redis.zrevrange(key, start, stop)

    def zscore(self, key, member):
        return self._redis.zscore(key, member)


class IConnection(object):
    CLIENT = IClient
    MASTER = None
    SLAVE = None

    @classmethod
    def connect_to_master(cls):
        return cls.CLIENT(**cls.MASTER)

    @classmethod
    def connect_to_slave(cls):
        if cls.SLAVE:
            connection_settings = cls.SLAVE
        else:
            connection_settings = cls.MASTER
        return cls.CLIENT(**connection_settings)
