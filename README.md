wishbone.output.redis
=====================


Write data to a redis server.
-----------------------------


    Creates a connection to a redis server and writes data to it.

    Parameters:

        - host(str)("localhost")
           | Redis hostname
        - port(int)(6379)
           | Redis port
        - database(int)(0)
           | Index of db to use
        - queue(str)("wishbone.out")
           | name of queue to push data to
        - key(str)("")
           | if event contains non-emtpy key value, push data to that queue
        - selection(str)("@data")
           |  The part of the event to submit externally.

    Queues:

        - inbox
           |  Data coming from the outside world.

Example:
--------

```yaml
---

modules:
  input:
    module: wishbone.input.redis

  mixing:
    module: wishbone.flow.roundrobin
    description: I roundrobin incoming messages
 
  modify1:
    module: wishbone.function.modify
    arguments:
      expressions:
         - set: [ "queue1", "redis_key" ]

  modify2:
    module: wishbone.function.modify
    arguments:
      expressions:
         - set: [ "queue2", "redis_key" ]

  funnel:
    module: wishbone.flow.funnel

  output:
    module: wishbone.output.redis
    arguments:
      key: redis_key

routingtable:
  - input.outbox   -> mixing.inbox
  - mixing.one     -> modify1.inbox
  - mixing.two     -> modify2.inbox
  - mixing.three   -> funnel.inbox
  - modify1.outbox -> funnel.inbox1
  - modify2.outbox -> funnel.inbox2
  - funnel.outbox  -> output.inbox

```

```bash
# Redis cli example
~> redis-cli
127.0.0.1:6379> FLUSHALL
OK
127.0.0.1:6379> LPUSH wishbone.in first
(integer) 1
127.0.0.1:6379> LPUSH wishbone.in second
(integer) 1
127.0.0.1:6379> LPUSH wishbone.in third
(integer) 1
127.0.0.1:6379> keys *
1) "queue1"
2) "queue2"
3) "wishbone.out"
127.0.0.1:6379> 
```
