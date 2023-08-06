'''
Introduction
------------

Redisext is a tool for data modeling. Its primary goal is to provide light
interface to well-known data models based on Redis such as queues, hashmaps,
counters, pools and stacks. Redisext could be treated as a ORM for Redis.

Tutorial
--------

Counter Model allows you to build counters in a minute. For example::

   import redisext.backend.redis
   import redisext.counter
   import redisext.serializer

   class Connection(redisext.backend.redis.Connection):
       MASTER = {'host': 'localhost', 'port': 6379, 'db': 0}

   class Visitors(Connection, redisext.counter.Counter):
       SERIALIZER = redisext.serializer.Numeric


This is it! You can start using it. Example of mythical frontpage view::

   def frontpage():
       visitors_counter = Visitors('fronpage')
       visitors_counter.increment()
       context = {
           'visitors': visitors_counter.get()
       }
       return context

.. note::

   Details on :class:`redisext.counter.Counter`.

Data Models
===========

.. automodule:: redisext.counter

.. automodule:: redisext.hashmap

.. automodule:: redisext.pool

.. automodule:: redisext.queue

.. automodule:: redisext.stack


Missed Imports
--------------

Imports section is intentionaly skiped, but for ther order it is listed below::

   import redisext.backend.redis
   import redisext.serializer

   class Connection(redisext.backend.redis.Connection):
      MASTER = {'host': 'localhost', 'port': 6379, 'db': 0}


Abstract Model
--------------

.. automodule:: redisext.models

.. automodule:: redisext.serializer

.. automodule:: redisext.key

.. automodule:: redisext.backend
'''

__version__ = '1.1.4'
