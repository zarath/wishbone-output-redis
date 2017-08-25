#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
redisout.py
==========

@author: "Holger Mueller" <holgerm1969@gmx.de>

Wishbone output module to connect with redis servers.
"""

from wishbone import Actor
from wishbone.event import Bulk
from gevent import socket as gsocket
import redis
import redis.connection

redis.connection.socket = gsocket


class RedisOut(Actor):
    '''**Send data to a redis server**

    Creates a connection to a redis server sends data to it.

    Parameters:

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

    Queues:

        - inbox
           |  Incoming events
    '''

    def __init__(self, actor_config,
                 host="localhost", port=6379, database=0,
                 queue="wishbone.out", key="", selection="@data", rpush=False):
        Actor.__init__(self, actor_config)
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
        '''Sets up redis connection'''
        self.conn = redis.Redis(host=self.redis_host, port=self.redis_port)
        self.conn.execute_command("SELECT " + str(self.redis_db))

        self.logging.info('Connection to %s created.' % self.redis_host)

        if self.rpush:
            self.pushcmd = self.conn.rpush
        else:
            self.pushcmd = self.conn.lpush

    def consume(self, event):
        '''Send data to redis queue'''

        if isinstance(event, Bulk):
            for evt in event.dump():
                dst = self._get_dest(evt)
                try:
                    data = evt.get(self.selection)
                except KeyError:
                    continue
                self.pushcmd(dst, data)
        else:
            dst = self._get_dest(event)
            self.pushcmd(dst, event.get(self.selection))

    def _get_dest(self, event):
        if self.key:
            try:
                return event.get(self.key)
            except KeyError:
                pass
        return self.queue
