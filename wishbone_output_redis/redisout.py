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

        - redisdb(dict){
            host(str): ("localhost"),  # Redis hostname
            port(int): (6379),         # Redis port
            database(int): (0),        # Index of db to use

        - queue(str)("wishbone.out")
           | name of queue to push data to
        - key(str)("")
           | if event contains non-emtpy key value, push data to that queue
        - selection(str)("@data")
           |  The part of the event to submit externally.

    Queues:

        - inbox
           |  Incoming events
    '''

    #pylint: disable=too-many-arguments
    def __init__(self, actor_config, redisdb=None,
                 queue="wishbone.out", key="", selection="@data"):
        Actor.__init__(self, actor_config)
        self.rdb = {
            'host': 'localhost',
            'port': 6379,
            'database': 0,
        }
        if redisdb:
            self.rdb.update(redis)
        self.queue = queue
        self.key = key
        self.selection = selection
        self.conn = None
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):
        '''Sets up redis connection'''
        self.conn = redis.Redis(host=self.rdb['host'], port=self.rdb['port'])
        self.conn.execute_command('SELECT', self.rdb['database'])

        self.logging.info('Connection to %s created.' % self.rdb['host'])

    def consume(self, event):
        '''Send data to redis queue'''

        if isinstance(event, Bulk):
            for evt in event.dump():
                dst = self._get_dest(evt)
                try:
                    data = evt.get(self.selection)
                except KeyError:
                    continue
                self.conn.lpush(dst, data)
        else:
            dst = self._get_dest(event)
            self.conn.lpush(dst, event.get(self.selection))

    def _get_dest(self, event):
        if self.key:
            try:
                return event.get(self.key)
            except KeyError:
                pass
        return self.queue
