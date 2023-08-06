"""
clients.redis
=============

Base functionality for accessing/modifying data in Redis.  Currently
the supported functionality is accessing Redis in a sharded manner.

"""
import collections
import logging
import os
import socket

from consistent_hash import ConsistentHash
import redis

try:
    from urllib.parse import parse_qs, urlsplit
except ImportError:
    from urlparse import parse_qs, urlsplit

version_info = (1, 0, 0)
__version__ = '.'.join(str(v) for v in version_info)

LOGGER = logging.getLogger(__name__)

DEFAULT_TTL = 24 * 60 * 60  # One day
DEFAULT_PORT = '6379'

_redis_config = collections.namedtuple('config', 'hosts port db ttl')
"""Container object for holding the exploded URI"""


class ShardedRedisConnection(object):
    """Maintain a list of several Redis backends in a sharded manner.

    This class establishes several pools based off of the IP addresses
    resolved from the ``hostname`` part of the ``REDIS_URI`` environment
    variable.  Any reads, writes, or deletes will be delegated to the proper
    Redis backend by determining which shard the query should be directed
    to.

    Additionally, the ``info`` method is available to gather health
    information across all of the servers in the backend.  This data can
    be used to determine the health of the service.

    .. note::

        The hostname in the ``REDIS_URI`` will be DNS resolved and a
        connection will be opened for each address returned in the
        answer section.  You can specify a Round-Robin DNS record and
        we will open a connection to all hosts returned.

    """

    def __init__(self):
        self.config = self._get_redis_config()
        self._connections = {}
        self._consistent_hash = ConsistentHash(self.config.hosts)
        self._establish_connections(self.config)

    def _get_redis_config(self):
        """Construct a Redis config object from the URI env-var."""
        LOGGER.debug(
            'Creating connection info for "%s"', os.environ['REDIS_URI'])

        broken = urlsplit(os.environ['REDIS_URI'])

        if broken.scheme != 'redis':
            raise RuntimeError('Non "redis://" URI provided in REDIS_URI!')

        _, _, ip_addresses = socket.gethostbyname_ex(broken.hostname)

        if not ip_addresses:
            raise RuntimeError('Unable to find Redis in DNS!')

        ttl = DEFAULT_TTL
        if broken.query:
            # parse_qs returns a list of values given a key
            ttl = parse_qs(broken.query).get('ttl', [ttl])[0]

        return _redis_config(
            hosts=ip_addresses,
            port=broken.port or DEFAULT_PORT,
            db=broken.path[1:],  # Remove the leading /
            ttl=int(ttl),
        )

    def _establish_connections(self, config):
        """Create Redis connection pool objects for each server shard."""
        LOGGER.debug('Establishing Redis connection pools')
        for host in config.hosts:
            LOGGER.debug('Opening Redis connection to host "%s"', host)
            self._connections[host] = redis.StrictRedis(
                host=host,
                port=config.port,
                db=config.db,
            )

    def _get_shard_connection(self, key):
        """Get a connection for a Redis shard given a ``key``."""
        LOGGER.debug('Getting Redis host shard given key "%s"', key)
        host = self._consistent_hash.get_node(key)
        LOGGER.debug('Got Redis host shard "%s" given key "%s"', host, key)
        return self._connections[host]

    def set(self, key, value, ttl=None):
        """Set ``key`` to ``value`` in a Redis shard."""
        LOGGER.debug('Setting Redis key "%s" to "%s"', key, value)
        ttl = ttl or self.config.ttl
        connection = self._get_shard_connection(key)
        connection.set(key, value, ex=ttl)

    def get(self, key):
        """Get a ``key`` in a Redis shard."""
        LOGGER.debug('Getting Redis value given key "%s"', key)
        connection = self._get_shard_connection(key)
        return connection.get(key)

    def delete(self, key):
        """Delete a ``key`` in a Redis shard."""
        LOGGER.debug('Deleting Redis key "%s"', key)
        connection = self._get_shard_connection(key)
        connection.delete(key)

    def info(self):
        """Return a list of the health of each connected redis server.

        :rtype: list
        :returns: A list of the server info from all of the server shards.

        """
        LOGGER.info('Getting Redis server stats')
        stats = []
        for host, connection in self._connections.items():
            LOGGER.debug('Getting Redis health for host "%s"', host)
            stats.append(connection.info())

        return stats
