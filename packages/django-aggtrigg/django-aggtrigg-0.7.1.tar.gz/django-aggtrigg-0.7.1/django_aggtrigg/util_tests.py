# -*- coding: utf-8 -*-

# Copyright (C) 2014 Rodolphe Quiedeville <rodolphe@quiedeville.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import six
import unittest
import util
import dbcommands
from mock import MagicMock

PGBACKEND = 'django.db.backends.postgresql_psycopg2'


class utilTests(unittest.TestCase):

    def setUp(self):
        self.agg = util.AggTrigger(PGBACKEND, 'foota', 'foocol', ['agg'])

    def test_init(self):
        self.assertEqual(self.agg.database, 'default')

    def test_agg_table_name(self):
        agg = util.AggTrigger(PGBACKEND, 'foota', 'foocol', ['agg'])
        self.assertTrue(agg.table_name, 'foota_foocol_agg')

    def test_function_name(self):
        self.assertEqual("foo_colfoo_insert()",
                         util.function_name('foo', 'colfoo', 'insert'))

    def test_trigger_name(self):
        self.assertEqual("foo_id_insert_insert_trigger",
                         util.trigger_name('foo', 'id',
                                           'foo_id_insert()', 'insert'))

    def test_sql_create_trigger(self):
        res = self.agg.sql_create_trigger('foo', 'insert', 'function_called()')
        sql = res[1]
        self.assertEqual(sql[:6], "CREATE")

    def test_sql_create_triggers(self):
        agg = util.AggTrigger(PGBACKEND, 'foota', 'foocol', ['agg'])
        res = agg.sql_create_triggers()
        self.assertEqual(len(res), 3)
        self.assertTrue(isinstance(res, list))

        tgnames = [tgn[0] for tgn in res]
        sqls = [tgn[1] for tgn in res]

        self.assertIn("foota_foocol_insert_insert_trigger", tgnames)
        self.assertEqual(sqls[0][:6], "CREATE")

    # def test_sql_create_function(self):
    #     agg = util.AggTrigger(PGBACKEND, 'foota', 'foocol', ['agg'])
    #     res = agg.sql_create_function('book', 'nbpage', ['count'], 'insert')
    #     self.assertTrue(isinstance(res, six.string_types))
    #     self.assertTrue(len(res) > 10)

    def test_sql_create_functions(self):
        agg = util.AggTrigger(PGBACKEND, 'foota', 'foocol', ['agg'])
        res = agg.sql_create_functions()
        self.assertTrue(isinstance(res, list))
        self.assertEqual(len(res), 3)

    def test_sql_drop_functions(self):
        agg = util.AggTrigger(PGBACKEND, 'foota', 'foocol', ['agg'])
        res = agg.sql_drop_functions()
        self.assertTrue(isinstance(res, list))
        self.assertEqual(len(res), 3)

    def test_sql_drop_triggers(self):
        agg = util.AggTrigger(PGBACKEND, 'foota', 'foocol', ['agg'])
        res = agg.sql_drop_triggers()
        self.assertTrue(isinstance(res, list))
        self.assertEqual(len(res), 3)

    def test_sql_create_table(self):
        """Test with only one aggregat
        """
        agg = util.AggTrigger(PGBACKEND, 'book', 'nbpage', ['count'])
        res = agg.sql_create_table()
        self.assertTrue(isinstance(res, six.string_types))
        self.assertTrue(len(res) > 3)

    def test_sql_create_table_twoagg(self):
        """Test with two aggregats
        """
        agg = util.AggTrigger(PGBACKEND, 'book', 'nbpage', ['count', 'min'])
        res = agg.sql_create_table()
        self.assertTrue(isinstance(res, six.string_types))
        self.assertTrue(len(res) > 3)

    def test_sql_drop_trigger(self):
        res = self.agg.sql_drop_trigger('foo', 'table_bar')
        self.assertTrue(isinstance(res, str))

    def test_sql_drop_function(self):
        res = self.agg.sql_drop_function('foo')
        self.assertTrue(isinstance(res, str))

    def test_sql_drop_table(self):
        res = self.agg.sql_drop_table()
        self.assertTrue(isinstance(res, str))

    def test_agg_create_table(self):
        agg = util.AggTrigger(PGBACKEND, 'book', 'nbpage', ['count'])
        dbcommands.execute_raw = MagicMock(return_value=0)
        res = agg.create_table()
        self.assertEqual(res, 0)

    def test_agg_create_triggers(self):
        agg = util.AggTrigger(PGBACKEND, 'book', 'nbpage', ['count'])
        dbcommands.execute_raw = MagicMock(return_value=0)
        res = agg.create_triggers()
        self.assertEqual(res, 0)

    def test_agg_create_functions(self):
        agg = util.AggTrigger(PGBACKEND, 'book', 'nbpage', ['count'])
        dbcommands.execute_raw = MagicMock(return_value=0)
        res = agg.create_functions()
        self.assertEqual(res, 0)

    def test_agg_create_objects(self):
        agg = util.AggTrigger(PGBACKEND, 'book', 'nbpage', ['count'])
        dbcommands.execute_raw = MagicMock(return_value=0)
        res = agg.create_objects()
        self.assertEqual(res, 0)

    def test_agg_sql_init(self):
        agg = util.AggTrigger(PGBACKEND, 'book', 'nbpage', ['count'])
        res = agg.sql_init()
        self.assertTrue(isinstance(res,
                                   six.string_types))

    def test_agg_functions_name(self):
        agg = util.AggTrigger(PGBACKEND, 'book', 'nbpage', ['count'])
        res = agg.functions_name
        self.assertTrue(res, ['book_nbpage_insert()',
                              'book_nbpage_update()',
                              'book_nbpage_delete()'])

    def test_functions_are_present(self):
        agg = util.AggTrigger(PGBACKEND, 'book', 'nbpage', ['count'])
        dbcommands.execute_raw = MagicMock(return_value=0)
        res = agg.functions_are_present()

        funcs = [fun[0] for fun in res]

        self.assertEqual(len(res), 3)
        self.assertEqual(funcs, ['book_nbpage_insert()',
                                 'book_nbpage_update()',
                                 'book_nbpage_delete()'])
