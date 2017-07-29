          __       __    __
.--.--.--|__.-----|  |--|  |--.-----.-----.-----.
|  |  |  |  |__ --|     |  _  |  _  |     |  -__|
|________|__|_____|__|__|_____|_____|__|__|_____|

Build composable event pipeline servers with minimal effort.

========================
wishbone.output.redis
========================


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
        - key(str)("queue")
           | name of queue to lpush data to

    Queues:

        - inbox
           |  Data coming from the outside world.
