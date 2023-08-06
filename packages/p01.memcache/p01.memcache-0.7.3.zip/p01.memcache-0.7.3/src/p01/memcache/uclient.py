##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: uclient.py 4101 2014-07-27 02:42:22Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import sys
import time
import types
import socket
import errno
import contextlib
import Queue
import logging
import cPickle
from hashlib import md5

import itertools
import threading

import umemcache

import zope.interface
from zope.schema.fieldproperty import FieldProperty

import p01.memcache.connector
from p01.memcache import interfaces

log = logging.getLogger('p01.memcache')

# empty slot marker with latest (maxint) priority
EMPTY_SLOT = (sys.maxint, None)



class UltraMemcacheClient(object):
    """Non persistent ultramemcached client usaable as global utility.

    This implementation supports open connection pooling and HA support with
    multiple servers pointing to different moxi instances.

    Note: this implementation uses a ultramemcached client including connection
    pooling instead of threading local client caching like the python memcache
    implementation. This means open connection ger reused between threads
    or greenlets. And yes this makes it fast and compatible with genvent.

    Important: if you use different memcached server for this client. They must
    provide key sharding. This client does not know how to shared your keys.
    Simply use a moxi server for each different server you use for this client.

    NOTE: the maxPoolSize only limits the max open connections managed in the
    pool. The client creates more connections if this limit is reached wich
    prevents to raise errors based on a connection limit. But such additional
    connections will get closed after they are not used anymore.

    """

    zope.interface.implements(interfaces.IUltraMemcacheClient)

    _memcacheClientFactory = umemcache.Client
    _connectorFactory = p01.memcache.connector.UltraConnector

    servers = FieldProperty(interfaces.IUltraMemcacheClient['servers'])
    debug = FieldProperty(interfaces.IUltraMemcacheClient['debug'])
    namespace = FieldProperty(interfaces.IUltraMemcacheClient['namespace'])
    pickleProtocol = FieldProperty(
        interfaces.IUltraMemcacheClient['pickleProtocol'])

    # connection setup
    timeout = FieldProperty(interfaces.IUltraMemcacheClient['timeout'])
    delay = FieldProperty(interfaces.IUltraMemcacheClient['delay'])
    retries = FieldProperty(interfaces.IUltraMemcacheClient['retries'])
    lifetime = FieldProperty(interfaces.IUltraMemcacheClient['lifetime'])

    # connection pool queue
    pooltime = FieldProperty(interfaces.IUltraMemcacheClient['pooltime'])
    maxPoolSize = FieldProperty(interfaces.IUltraMemcacheClient['maxPoolSize'])

    # server handling
    blacktime = FieldProperty(interfaces.IUltraMemcacheClient['blacktime'])

    def __init__(self, servers=['127.0.0.1:11211'], debug=0, pickleProtocol=-1,
        lifetime=3600, namespace=None, timeout=3, delay=1, retries=3,
        pooltime=60, blacktime=60, maxPoolSize=50):
        # only use multiple server if they know how to shared keys! (e.g. moxi)
        self.servers = servers
        if len(servers) < 1:
            raise ValueError("Must at least provide one or more servers")
        if len(servers) == 1:
            self._single_server = servers[0]
            self._servers = None
        else:
            self._single_server = None
            self._servers = itertools.cycle(servers)
        self._blacklist = []
        self.debug = debug
        self.pickleProtocol = pickleProtocol
        if lifetime is None:
            lifetime = 0
        self.lifetime = lifetime
        if namespace is not None:
            self.namespace = namespace

        # pool
        self.maxPoolSize = maxPoolSize
        self.pooltime = pooltime
        self.blacktime = blacktime
        self.timeout = timeout
        self.pool = Queue.PriorityQueue(self.maxPoolSize)
        # If there is a maxPoolSize, prime the queue with empty slots.
        if maxPoolSize is not None:
            for _ in xrange(maxPoolSize):
                self.pool.put(EMPTY_SLOT)

        # server blacklist
        self._blacklist = {}
        self.retries = retries
        self._pick_index = 0
        self._lock = threading.Lock()

    def updateBlacklist(self, server=None):
        """Bring server back from blacklist"""
        if server is not None:
            # add given server to blacklist
            with self._lock:
                self._blacklist[server] = time.time()
        now = time.time()
        for key, age in self._blacklist.items():
            if now - age > self.blacktime:
                with self._lock:
                    # remove from blacklist
                    del self._blacklist[key]

    def _getServer(self):
        """Get a (memcached or moxi) server or None

        NOTE: this client implementation doesn't support key sharding. You
        must point your different server to moxi instances which knows how to
        shared keys.
        """
        if self._single_server:
            server = self._single_server
        else:
            # robin round from server (cycle) generator
            with self._lock:
                # generator are not threadsafe, use lock
                server = self._servers.next()
        # check blacklist
        if server in self._blacklist:
            return None
        else:
            return server

    # connector pool handling
    def _getConnector(self):
        server = self._getServer()
        if not server:
            # refresh blacklisted
            self.updateBlacklist()
            # and try again
            server = self._getServer()
        last_error = None

        def createConnector(server):
            return self._connectorFactory(self._memcacheClientFactory,
                server, debug=self.debug, timeout=self.timeout,
                retries=self.retries, delay=self.delay)

        while server is not None:
            connector = createConnector(server)
            try:
                connector.connect()
                return connector
            except (socket.timeout, socket.error), e:
                if not isinstance(e, socket.timeout):
                    if e.errno != errno.ECONNREFUSED:
                        raise

                # blacklist this server and try again
                self.updateBlacklist(server)
                server = self._getServer()
                last_error = e

        if last_error is not None:
            raise last_error
        else:
            raise socket.timeout('No memcached server left in the pool')

    def _checkout_connection(self):
        # we only wait if we have a max pool size
        blocking = self.maxPoolSize is not None
        # Loop until we get a non-stale connection, or we create a new one.
        while True:
            try:
                # get the next connector and block (depends on max pool size)
                ts, connector = self.pool.get(blocking)
            except Queue.Empty:
                # no max pool size defined and queue is empty, jsut create one
                now = int(time.time())
                return now, self._getConnector()
            else:
                now = int(time.time())
                # If we got an empty slot placeholder, create a new connection.
                if connector is None:
                    try:
                        # and return
                        return now, self._getConnector()
                    except Exception, e:
                        if self.maxPoolSize is not None:
                            # return slot to queue
                            self.pool.put(EMPTY_SLOT)
                        raise e
                # if the connection is not stale, go ahead and use it.
                if ts + self.pooltime > now:
                    return ts, connector
                # Otherwise, the connection is stale.
                # Close it, push an empty slot onto the queue, and retry.
                connector.disconnect()
                self.pool.put(EMPTY_SLOT)
                continue

    def _checkin_connection(self, ts, connector):
        """Return a connection to the pool."""
        try:
            # If the connection is now stale, don't return it to the pool.
            # Push an empty slot instead so that it will be refreshed when needed.
            now = int(time.time())
            if ts + self.pooltime > now:
                # return the connector to the pool
                self.pool.put((ts, connector))
            else:
                if self.maxPoolSize is not None:
                    self.pool.put(EMPTY_SLOT)
        except Queue.Full:
            # we just returned an additional connection to the pool
            pass

    @contextlib.contextmanager
    def connector(self):
        """Get a connector from the pool (queue)"""
        ts, connector = self._checkout_connection()
        try:
            yield connector
        finally:
            self._checkin_connection(ts, connector)

    # client api
    def buildKey(self, key):
        """Builds a (md5) memcache key based on the given key

        - if the key is a string, the plain key get used as base

        - if the key is unicode, the key get converted to UTF-8 as base

        - if the key is an int, the key get converted to string as base

        - if key is a persistent object its _p_oid is used as base

        - anything else will get pickled (including unicode)

        Such a base key get converted to an md5 hexdigest if a namespace is
        used, the namespace is used as key prefix.

        """
        if isinstance(key, (types.IntType, types.StringType)):
            bKey = str(key)
        elif isinstance(key, types.UnicodeType):
            bKey = key.encode('UTF-8')
        elif getattr(key, '_p_oid', None):
            bKey = getattr(key, '_p_oid')
        else:
            bKey = cPickle.dumps(key, protocol=self.pickleProtocol)

        if self.namespace is not None:
            bKey = '%s%s' % (self.namespace, bKey)
        mKey = md5(bKey)
        return mKey.hexdigest()

    def set(self, key, data, lifetime=0, raw=False):
        bKey = self.buildKey(key)
        if not lifetime:
            lifetime = self.lifetime
        if raw:
            if not isinstance(data, types.StringType):
                raise ValueError(
                    "Data must be a string %s given" % type(data), data)
        else:
            data = cPickle.dumps(data, protocol=self.pickleProtocol)
        if self.debug:
            log.debug('set: %r -> %s, %r, %r, %r' % (key, bKey, len(data),
                self.namespace, lifetime))

        with self.connector() as conn:
            if conn.set(bKey, data, lifetime):
                return bKey

        return None

    def query(self, key, raw=False, default=None):
        bKey = self.buildKey(key)
        with self.connector() as conn:
            res = conn.get(bKey)
            if res is not None and self.debug:
                log.debug('query: %r, %r, %r, %r' % (key, len(res), self.namespace,
                    raw))
            if res is None:
                return default
            if raw:
                return res
            return cPickle.loads(res)

    def invalidate(self, key):
        bKey = self.buildKey(key)
        if self.debug:
            log.debug('invalidate: %r -> %s, %r '% (key, bKey, self.namespace))
        with self.connector() as conn:
            conn.delete(bKey)

    def invalidateAll(self):
        if self.debug:
            log.debug('invalidateAll')
        with self.connector() as conn:
            conn.flush_all()

    def getStatistics(self):
        with self.connector() as conn:
            return conn.get_stats()
