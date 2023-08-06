#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cassandra Stress Test

Usage:
  stresstest [--port=<number>] [--keyspace=<name>] [--keys=<num>] [--size=<bytes>] [--ttl=<secs>] [--replication=<num>] [--timeout=<secs>] <servers>...
  stresstest -h | --help
  stresstest -v | --version

Options:
  -h --help            Show this screen.
  -v --version         Show version.
  <servers>            Cassandra Server IP addresses
  --port=<number>      Cassandra port [default: 9042]
  --keyspace=<name>    Keyspace name [default: test]
  --keys=<num>         Number of keys to insert into keyspace [default: 100]
  --size=<bytes>       Size in bytes of value [default: 1024]
  --ttl=<secs>         Time to live for keys in seconds [default: never]
  --replication=<num>  Replication Factor number [default: 2]
  --timeout=<secs>     Timeout seconds for queries before failure [default: 10.0]
"""
from docopt import docopt
import sys

from cassandra.cluster import Cluster
from cassandra.io.libevreactor import LibevConnection
from cassandra.protocol import ConfigurationException


class Connection(object):
    def __init__(self, servers, port, keyspace, replication, timeout):
        self.cluster = Cluster(servers, port=port)
        self.cluster.connection_class = LibevConnection
        self.session = self.cluster.connect()
        self.timeout = timeout
        self.create_keyspace(keyspace, replication)
        self.create_table()

    def create_keyspace(self, keyspace, replication):
        query = "CREATE KEYSPACE {0} WITH replication = {'class':'SimpleStrategy', 'replication_factor': {1}};".format(keyspace, replication)
        self.session.execute(create_keyspace_query, timeout=self.timeout)
        self.session.set_keyspace(keyspace)

    def create_table(self, ):
        self.session.execute("""CREATE TABLE stresstest (
                                id int PRIMARY KEY,
                                value text
                                );""",
                                timeout=self.timeout)

    def insert(key, value, ttl=None):
        create_query = """INSERT INTO stresstest (id, value)
                          VALUES (%s, %s)
                       """
        if ttl is not None:
            create_query += " USING TTL {0}; ".format(ttl)
        self.session.execute(create_query, (key, value), timeout=self.timeout)

    def close(self):
        self.session.cluster.shutdown()
        self.session.shutdown()


def key_factory(num):
    for i in range(num):
        yield i


def value(size):
    return bytearray(size)


def main():
    args = docopt(__doc__, version='1.0', options_first=True)
    servers = args['<servers>']
    port = int(args['--port'])
    keyspace = args['--keyspace']
    keys = int(args['--keys'])
    size = int(args['--size'])
    try:
        ttl = float(args['--ttl'])
    except ValueError:
        ttl = None
    replication = int(args['--replication'])
    timeout = float(args['--timeout'])

    cxn = Connection(servers, port, keyspace, replication, timeout)
    v = value(size)
    for key in key_factory(num):
        cxn.insert(key, v, ttl)
    cxn.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
