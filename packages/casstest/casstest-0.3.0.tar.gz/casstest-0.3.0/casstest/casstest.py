# -*- coding: utf-8 -*-
import os
import uuid
from cassandra.io.libevreactor import LibevConnection
from cassandra.cluster import Cluster


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

    print('Using keyspace {0}'.format(keyspace))
    session = cluster.connect(keyspace)

    user_id = uuid.uuid1()
    create_query = """
                INSERT INTO users (name, age, user_id)
                VALUES (%s, %s, %s)
                """, ("John O'Reilly", 42, user_id)

    session.execute(create_query)
    test_read(session, user_id, 42)

    update_query = 'UPDATE users SET age = 84'
    session.execute(update_query)
    test_read(session, user_id, 84)

    delete_query = 'DELETE name, age, user_id FROM users'
    session.execute(delete_query)


if __name__ == '__main__':
    main()
