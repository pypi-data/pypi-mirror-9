Redisext
========

.. image:: https://travis-ci.org/mylokin/redisext.svg?branch=master
   :target: https://travis-ci.org/mylokin/redisext

.. image:: https://pypip.in/wheel/redisext/badge.svg
   :target: https://pypi.python.org/pypi/redisext/

.. image:: https://pypip.in/d/redisext/badge.png
   :target: https://crate.io/packages/redisext/

Documentation
-------------

Documentation is available at https://pythonhosted.org/redisext/.

Example
-------

Data model example:

.. code-block:: python

   import redisext.backend.redis
   import redisext.hashmap
   import redisext.serializer


   class Connection(redisext.backend.redis.Connection):
       MASTER = {'host': 'localhost', 'port': 6379, 'db': 0}


   class SeriousStats(Connection, redisext.hashmap.Map):
       SERIALIZER = redisext.serializer.Numeric
