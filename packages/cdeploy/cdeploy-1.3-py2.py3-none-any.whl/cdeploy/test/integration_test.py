import unittest
import os
from cassandra.cluster import Cluster

cluster = Cluster(['cassandra.local'])
session = cluster.connect()


def reset_db(keyspace):
    session.execute('DROP KEYSPACE IF EXISTS {0}'.format(keyspace))
    session.execute("""
        CREATE KEYSPACE """ + keyspace + """
            WITH replication =
                {'class': 'SimpleStrategy', 'replication_factor': '1'}
    """)


def run_migrator(arg=''):
    test_dir = os.path.dirname(os.path.realpath(__file__))
    os.system(
        'cd {0}/..; python migrator.py test/migrations {1}'.format(test_dir,
                                                                   arg)
    )


def do_undo():
    run_migrator('--undo')


class FirstRunTest(unittest.TestCase):
    def setUp(self):
        os.unsetenv('ENV')
        reset_db('migrations_development')

    def test_migrations_applied(self):
        run_migrator()
        result = session.execute(
            'SELECT * FROM migrations_development.schema_migrations LIMIT 1'
        )
        self.assertEquals(result[0].version, 2)


class UndoTest(unittest.TestCase):
    def setUp(self):
        os.unsetenv('ENV')
        reset_db('migrations_development')

    def test_undo(self):
        run_migrator()
        do_undo()
        result = session.execute(
            'SELECT * FROM migrations_development.schema_migrations LIMIT 1'
        )
        self.assertEquals(result[0].version, 1)


class DatabaseEnvironmentsTest(unittest.TestCase):
    def setUp(self):
        reset_db('migrations_test')

    def tearDown(self):
        os.unsetenv('ENV')

    def test_changing_env(self):
        os.putenv('ENV', 'test')
        run_migrator()
        result = session.execute(
            'SELECT * FROM migrations_test.schema_migrations LIMIT 1'
        )
        self.assertEquals(result[0].version, 2)


if __name__ == '__main__':
    unittest.main()
