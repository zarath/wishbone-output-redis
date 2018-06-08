#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
redisout.py.

@author: "Holger Mueller" <holgerm1969@gmx.de>

Wishbone output module to connect with redis servers.
"""

from wishbone.module import OutputModule
from wishbone.event import extractBulkItems
from gevent import socket as gsocket
import redis
import redis.connection

redis.connection.socket = gsocket


class RedisOut(OutputModule):
    """Send data to a redis server.

    Creates a connection to a redis server sends data to it.

    Parameters
    ----------
        - host(str)("localhost")
           |  Redis hostname
        - port(int)(6379)
           | Redis port
        - database(int)(0)
           | Index of db to use
        - queue(str)("wishbone.out")
           | name of queue to push data to
        - key(str)("")
           | if event contains non-emtpy key value, push data to that queue
        - selection(str)("@data")
           | The part of the event to submit externally.
        - rpush(bool)(False)
           | use rpush instead of lpush

    Queues
    ------
        - inbox
           |  Incoming events

    """

    def __init__(
            self,
            actor_config,
            host="localhost",
            port=6379,
            database=0,
            queue="wishbone.out",
            key="",
            native_events=False,
            payload=None,
            parallel_streams=1,
            selection="@data",
            rpush=False
            ):
        """Output module to redis database."""
        OutputModule.__init__(self, actor_config)
        self.redis_host = host
        self.redis_port = port
        self.redis_db = database
        self.queue = queue
        self.key = key
        self.selection = selection
        self.conn = None
        self.rpush = rpush
        self.pushcmd = None
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):
        """Set up redis connection."""
        self.conn = redis.StrictRedis(
            host=self.redis_host, port=self.redis_port, db=self.redis_db)
        self.logging.info('Connection to %s created.' % self.redis_host)

        if self.rpush:
            self.pushcmd = self.conn.rpush
        else:
            self.pushcmd = self.conn.lpush

    def _extract_event(self, event):
        try:
            data = event.get(self.selection)
            destination = self._get_dest(event)
            return (data, destination)
        except KeyError:
            return (False, False)

    def consume(self, event):
        """Send data to redis queue."""
        try:
            if event.isBulk():
                for evt in extractBulkItems(event):
                    data, dst = self._extract_event(evt)
                    if not data:
                        continue
                    self.pushcmd(dst, data)
            else:
                data, dst = self._extract_event(event)
                if not data:
                    return
                self.pushcmd(dst, event.get(self.selection))
                self.logging.warn("Added data to redis: {}".format(data))
        except Exception as error:
                self.logging.crit(
                    "Falied to set key in Redis. Reason: {}".format(error)
                    )

    def _get_dest(self, event):
        if self.key:
            try:
                return event.get(self.key)
            except KeyError:
                pass
        return self.queue
