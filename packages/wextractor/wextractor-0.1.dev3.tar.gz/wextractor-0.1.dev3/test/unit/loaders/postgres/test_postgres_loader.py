import unittest
from mock import Mock, patch
from nose.tools import raises
from wextractor.loaders.postgres import PostgresLoader

class TestPostgresLoader(unittest.TestCase):
    def setUp(self):
        self.loader = PostgresLoader({'database': 'dummy_db', 'user': 'dummy_user'})

        self.loader_with_tables = PostgresLoader(
            {'database': 'dummy_db', 'user': 'dummy_user'},
            schema=[{'table_name': 'test', 'pkey': 'id', 'columns': (('id', 'INTEGER'),)}]
        )

        self.table_schema = {
            'table_name': 'test', 'pkey': 'id', 'columns': (('id', 'INTEGER'),)
        }
        self.table_schema_no_pkey = {
            'table_name': 'test', 'columns': (('id', 'INTEGER'),)
        }
        self.table_schema_cols_not_tuple = {
            'table_name': 'test', 'pkey': 'id', 'columns': (('id'))
        }
        self.table_schema_no_col_types = {
            'table_name': 'test', 'pkey': 'id', 'columns': (('id',),)
        }
        self.table_schema_no_cols = {
            'table_name': 'test', 'pkey': 'id'
        }

    def test_init_postgres_failures(self):
        '''Tests that having no pkey raises an Exception'''
        self.assertRaises(Exception, PostgresLoader.__init__, ({'database': 'dummy_db', 'user': 'dummy_user'}, self.table_schema_no_cols))
        self.assertRaises(Exception, PostgresLoader.__init__, ({'database': 'dummy_db', 'user': 'dummy_user'}, self.table_schema_cols_not_tuple))
        self.assertRaises(Exception, PostgresLoader.__init__, ({'database': 'dummy_db', 'user': 'dummy_user'}, self.table_schema_no_col_types))
        self.assertRaises(Exception, PostgresLoader.__init__, ({'database': 'dummy_db', 'user': 'dummy_user'}, self.table_schema_no_pkey))

    def test_generate_drop_table_query(self):
        '''
        Tests that the drop query is created properly
        '''
        drop_table_query = self.loader.generate_drop_table_query(self.table_schema)
        self.assertEquals(drop_table_query, 'DROP TABLE IF EXISTS test CASCADE')

    def test_generate_table_schema(self):
        '''
        Tests that the create query is created properly
        '''
        create_table_query = self.loader.generate_create_table_query(self.table_schema)
        self.assertEquals(
            create_table_query,
            'CREATE TABLE IF NOT EXISTS test (row_id SERIAL,id INTEGER, PRIMARY KEY(id))'
        )

    def test_generate_alter_table_query(self):
        '''
        Tests that the alter query is created properly
        '''
        self.assertTrue(
            self.loader.generate_foreign_key_query(self.table_schema) is None
        )


    @patch('psycopg2.connect')
    def test_connect_method(self, connect):
        '''
        Ensures that the postgres loader will raise an exception if the connection string is malformed
        '''
        no_user_loader = PostgresLoader({'database': 'dummy_db'})
        no_db_loader = PostgresLoader({'user': 'dummy_user'})

        self.assertRaises(Exception, no_user_loader.connect)
        self.assertRaises(Exception, no_db_loader.connect)

        # assert that the proper one doesn't blow up
        self.loader.connect()

    @patch('wextractor.loaders.postgres.PostgresLoader.connect')
    def test_load_calls_connect(self, PostgresLoader):
        '''
        Mocks the class connect method, ensures it is called
        '''
        self.loader_with_tables.load([], True)

        assert self.loader.connect.called

    def test_null_replace(self):
        '''
        Tests to make sure that nulls are properly replaced
        '''
        self.assertEquals(self.loader.null_replace(''), 'NULL')
        self.assertEquals(self.loader.null_replace(u''), 'NULL')
        self.assertEquals(self.loader.null_replace(None), 'NULL')

    @patch('wextractor.loaders.postgres.PostgresLoader.connect')
    def test_md5_hash(self, PostgresLoader):
        '''
        Tests to make sure the md5 hash is working properly
        '''
        self.loader_with_tables.hash_row = Mock(return_value='foo')
        self.loader_with_tables.load([{'id': 1}], True)

        assert self.loader_with_tables.hash_row.called