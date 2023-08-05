import os
import unittest
try:
    from unittest import mock  # pylint: disable-msg=E0611
except ImportError:
    import mock

from cdeploy import migrator
from cdeploy import cqlexecutor


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_MIGRATIONS_PATH = os.path.join(TEST_DIR, './migrations')

migration_1_content = open(
    os.path.join(TEST_MIGRATIONS_PATH, '001_create_users.cql')
).read()
migration_2_content = open(
    os.path.join(TEST_MIGRATIONS_PATH, '002_add_firstname.cql')
).read()


class ApplyingMigrationTests(unittest.TestCase):
    def setUp(self):
        self.session = mock.Mock()
        self.migrator = migrator.Migrator(TEST_MIGRATIONS_PATH, self.session)
        self.migrator.get_top_version = mock.Mock(return_value=0)

    def test_it_should_make_sure_the_schema_migrations_table_exists(self):
        cqlexecutor.CQLExecutor.init_table = mock.Mock()
        self.migrator.run_migrations()
        cqlexecutor.CQLExecutor.init_table.assert_called_once_with(
            self.session
        )

    def test_it_should_initially_apply_all_the_migrations(self):
        cqlexecutor.CQLExecutor.execute = mock.Mock()
        self.migrator.run_migrations()
        cqlexecutor.CQLExecutor.execute.assert_has_calls([
            mock.call(self.session, migration_1_content),
            mock.call(self.session, migration_2_content)
        ])

    def test_it_should_add_migration_versions_to_schema_migrations_table(self):
        cqlexecutor.CQLExecutor.add_schema_migration = mock.Mock()
        self.migrator.run_migrations()

        cqlexecutor.CQLExecutor.add_schema_migration.assert_has_calls([
            mock.call(self.session, 1),
            mock.call(self.session, 2)
        ])

    def test_it_should_only_run_migrations_that_have_not_been_applied(self):
        cqlexecutor.CQLExecutor.execute = mock.Mock()
        self.migrator.get_top_version = mock.Mock(return_value=1)
        self.migrator.run_migrations()

        cqlexecutor.CQLExecutor.execute.assert_called_once_with(
            self.session,
            migration_2_content
        )


class UndoMigrationTests(unittest.TestCase):
    def setUp(self):
        self.session = mock.Mock()
        self.migrator = migrator.Migrator(TEST_MIGRATIONS_PATH, self.session)
        self.migrator.get_top_version = mock.Mock(return_value=2)

    def test_it_should_rollback_the_schema_version(self):
        cqlexecutor.CQLExecutor.rollback_schema_migration = mock.Mock()
        self.migrator.undo()
        cqlexecutor.CQLExecutor.rollback_schema_migration. \
            assert_called_once_with(self.session)

    def test_it_should_rollback_version_2(self):
        cqlexecutor.CQLExecutor.execute_undo = mock.Mock()
        self.migrator.undo()
        cqlexecutor.CQLExecutor.execute_undo.assert_called_once_with(
            self.session,
            migration_2_content
        )

    def test_it_should_do_nothing_if_at_version_0(self):
        self.migrator.get_top_version = mock.Mock(return_value=0)
        cqlexecutor.CQLExecutor.execute_undo = mock.Mock()
        self.migrator.undo()
        self.assertFalse(cqlexecutor.CQLExecutor.execute_undo.called)


class TopSchemaVersionTests(unittest.TestCase):
    def setUp(self):
        self.session = mock.Mock()
        self.migrator = migrator.Migrator(TEST_MIGRATIONS_PATH, self.session)

    def test_it_should_return_zero_initially(self):
        cqlexecutor.CQLExecutor.get_top_version = mock.Mock(return_value=[])

        self.assertEquals(0, self.migrator.get_top_version())

    def test_it_should_return_the_highest_version_from_schema_migrations(self):
        cqlexecutor.CQLExecutor.get_top_version = \
            mock.Mock(return_value=[mock.Mock(version=7)])
        version = self.migrator.get_top_version()

        self.assertEquals(version, 7)


if __name__ == '__main__':
    unittest.main()
