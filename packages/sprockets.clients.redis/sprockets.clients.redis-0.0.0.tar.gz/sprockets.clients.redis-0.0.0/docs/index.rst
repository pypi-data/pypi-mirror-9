sprockets.clients.redis
=======================
Base functionality for accessing/modifying data in Redis

|Version| |Downloads| |Status| |Coverage| |License|

Installation
------------
``sprockets.clients.redis`` is available on the
`Python Package Index <https://pypi.python.org/pypi/sprockets.clients.redis>`_
and can be installed via ``pip`` or ``easy_install``:

.. code:: bash

  pip install sprockets.clients.redis

Requirements
------------

* ``consistent_hash==1.0``
* ``hiredis==0.1.6``
* ``redis==2.10.3``

Simple Example
--------------

Simple CRUD operations on a key.

.. code:: python

    >>> import os
    >>> os.environ['REDIS_URI'] = 'redis://localhost/'

    >>> shard = ShardedRedisConnection()
    <sprockets.clients.redis.ShardedRedisConnection at 0x1046f2c90>

    >>> shard.set('foo', 1)
    >>> shard.get('foo')
    '1'
    >>> shard.delete('foo')
    >>> value = shard.get('foo')
    >>> value is None
    True

Setting a TTL on your key.

.. code:: python

    >>> import os
    >>> import time
    >>> os.environ['REDIS_URI'] = 'redis://localhost/'

    >>> shard = ShardedRedisConnection()
    <sprockets.clients.redis.ShardedRedisConnection at 0x1046f2c90>

    >>> shard.set('bar', 1, ttl=2)
    >>> shard.get('bar')
    '1'
    >>> time.sleep(2)
    >>> value = shard.get('foo')
    >>> value is None
    True

API Documentation
-----------------
.. toctree::
   :maxdepth: 2

   api
   history
   contributing

Version History
---------------
See :doc:`history`

Contributing
------------
Issues and Pull Requests are always welcome.  For more information on how to contribute
please refer to :doc:`contributing`.

Issues
------
Please report any issues to the Github project at `https://github.com/sprockets/sprockets.clients.redis/issues <https://github.com/sprockets/sprockets.clients.redis/issues>`_

Source
------
``sprockets.clients.redis`` source is available on Github at `https://github.com/sprockets/sprockets.clients.redis <https://github.com/sprockets/sprockets.clients.redis>`_

License
-------
``sprockets.clients.redis`` is released under the `3-Clause BSD license <https://github.com/sprockets/sprockets.clients.redis/blob/master/LICENSE>`_.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

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
