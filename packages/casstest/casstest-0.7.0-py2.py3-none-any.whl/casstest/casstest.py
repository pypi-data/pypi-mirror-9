# -*- coding: utf-8 -*-
import os
import uuid
from cassandra import InvalidRequest
from cassandra.cluster import Cluster
from cassandra.io.libevreactor import LibevConnection
from cassandra.protocol import ConfigurationException


seed = os.environ.get('SEED', '127.0.0.1')
port = int(os.environ.get('PORT', '9042'))
keyspace = os.environ.get('KEYSPACE', 'test')


def test_read(session, user_id, age):
    read_query = 'SELECT name, age, user_id FROM users'
    rows = session.execute(read_query)
    for row in rows:
        assert(row.name == "John O'Reilly")
        assert(row.age == age)
        assert(row.user_id == user_id)


def main():
    print('Connecting to seed {0} on port {1}'.format(seed, port))

    cluster = Cluster([seed], port=port)
    cluster.connection_class = LibevConnection
    session = cluster.connect()
    print('Dropping keyspace {0}'.format(keyspace))
    try:
        session.execute('DROP KEYSPACE {0}'.format(keyspace))
    except ConfigurationException:
        pass

    print('Creating keyspace {0}'.format(keyspace))
    create_keyspace_query = "CREATE KEYSPACE %s WITH replication = {'class':'SimpleStrategy', 'replication_factor':3};" % keyspace
    session.execute(create_keyspace_query)

    print('Using keyspace {0}'.format(keyspace))
    session.set_keyspace(keyspace)

    print('Dropping table users from keyspace {0}'.format(keyspace))

    try:
       session.execute("""DROP TABLE users""")
    except InvalidRequest:
       pass

    session.execute("""
    CREATE TABLE users (
        user_id uuid PRIMARY KEY,
        name text,
        age int,
    );
    """)

    user_id = uuid.uuid1()
    create_query = """
                   INSERT INTO users (name, age, user_id)
                   VALUES (%s, %s, %s)
                   """

    print('Creating')
    session.execute(create_query, ("John O'Reilly", 42, user_id))

    print('Reading')
    test_read(session, user_id, 42)

    print('Updating')
    update_query = 'UPDATE users SET age = 84 WHERE user_id = %s'
    session.execute(update_query, [user_id])
    test_read(session, user_id, 84)

    print('Deleting')
    delete_query = 'DELETE name, age FROM users where user_id = %s'
    session.execute(delete_query, [user_id])

    print('Dropping keyspace {0}'.format(keyspace))
    session.execute('DROP KEYSPACE %s' % keyspace)
    session.cluster.shutdown()
    session.shutdown()
    print('Success!')

if __name__ == '__main__':
    main()
