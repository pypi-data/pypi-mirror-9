sprockets.clients.redis
=======================
Base functionality for accessing/modifying data in Redis.  Currently
there is only support for interacting with Redis servers in a sharded
manner.

That is to say, there are multiple Redis servers we are distributing reads
and writes among them based on a consistent hash of the key value we're
operating on.  This is also known as "Client Side Partitioning".

More information about setting up or managing Redis in this manner
can be found on the Redis documentation website: http://redis.io/topics/partitioning

|Version| |Downloads| |Status| |Coverage| |License|

Installation
------------
``sprockets.clients.redis`` is available on the
`Python Package Index <https://pypi.python.org/pypi/sprockets.clients.redis>`_
and can be installed via ``pip`` or ``easy_install``:

.. code:: bash

  pip install sprockets.clients.redis

Documentation
-------------
https://sprocketsclientsredis.readthedocs.org

Requirements
------------
.. include:: requirements.txt

Example
-------
This examples demonstrates how to use a sharded Redis connection
in ``sprockets.clients.redis`` by ...

.. code:: python

    import os
    from sprockets import clients.redis

    os.environ['REDIS_URI'] = 'redis://localhost/'

    shard = clients.redis.ShardedRedisConnection()

    shard.set('foo', 1)
    value = shard.get('foo')
    shard.delete('foo')


Version History
---------------
Available at https://sprocketsclientsredis.readthedocs.org/en/latest/history.html

.. |Version| image:: https://badge.fury.io/py/sprockets.clients.redis.svg?
   :target: http://badge.fury.io/py/sprockets.clients.redis

.. |Status| image:: https://travis-ci.org/sprockets/sprockets.clients.redis.svg?branch=master
   :target: https://travis-ci.org/sprockets/sprockets.clients.redis

.. |Coverage| image:: https://img.shields.io/coveralls/sprockets/sprockets.clients.redis.svg?
   :target: https://coveralls.io/r/sprockets/sprockets.clients.redis

.. |Downloads| image:: https://pypip.in/d/sprockets.clients.redis/badge.svg?
   :target: https://pypi.python.org/pypi/sprockets.clients.redis

.. |License| image:: https://pypip.in/license/sprockets.clients.redis/badge.svg?
   :target: https://sprocketsclientsredis.readthedocs.org
