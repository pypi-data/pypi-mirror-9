# -*- coding: utf-8 -*-
"""Test indexes"""

import pytest

from pyrseas.testutils import DatabaseToMapTestCase
from pyrseas.testutils import InputMapToSqlTestCase, fix_indent

CREATE_TABLE_STMT = "CREATE TABLE t1 (c1 integer, c2 text)"
CREATE_STMT = "CREATE INDEX t1_idx ON t1 (c1)"
COMMENT_STMT = "COMMENT ON INDEX t1_idx IS 'Test index t1_idx'"


class IndexToMapTestCase(DatabaseToMapTestCase):
    """Test mapping of created indexes"""

    def test_index_1(self):
        "Map a single-column index"
        dbmap = self.to_map([CREATE_TABLE_STMT, CREATE_STMT])
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'text'}}],
                  'indexes': {'t1_idx': {'keys': ['c1']}}}
        assert dbmap['schema public']['table t1'] == expmap

    def test_index_2(self):
        "Map a two-column index"
        stmts = ["CREATE TABLE t1 (c1 INTEGER, c2 CHAR(5), c3 TEXT)",
                 "CREATE UNIQUE INDEX t1_idx ON t1 (c1, c2)"]
        dbmap = self.to_map(stmts)
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'character(5)'}},
                              {'c3': {'type': 'text'}}],
                  'indexes': {'t1_idx': {'keys': ['c1', 'c2'],
                                         'unique': True}}}
        assert dbmap['schema public']['table t1'] == expmap

    def test_index_3(self):
        "Map a table with a unique index and a non-unique GIN index"
        stmts = ["CREATE TABLE t1 (c1 INTEGER, c2 CHAR(5), c3 tsvector)",
                 "CREATE UNIQUE INDEX t1_idx_1 ON t1 (c1, c2)",
                 "CREATE INDEX t1_idx_2 ON t1 USING gin (c3)"]
        dbmap = self.to_map(stmts)
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'character(5)'}},
                              {'c3': {'type': 'tsvector'}}],
                  'indexes': {'t1_idx_1': {'keys': ['c1', 'c2'],
                                           'unique': True},
                              't1_idx_2': {'keys': ['c3'],
                                           'access_method': 'gin'}}}
        assert dbmap['schema public']['table t1'] == expmap

    def test_map_index_partial(self):
        "Map a table with a partial index"
        dbmap = self.to_map([CREATE_TABLE_STMT,
                             "CREATE INDEX t1_idx ON t1 (c2) WHERE c1 > 42"])
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'text'}}],
                  'indexes': {'t1_idx': {'keys': ['c2'],
                                         'predicate': '(c1 > 42)'}}}
        assert dbmap['schema public']['table t1'] == expmap

    def test_index_function(self):
        "Map an index using a function"
        stmts = [CREATE_TABLE_STMT, "CREATE INDEX t1_idx ON t1 ((lower(c2)))"]
        dbmap = self.to_map(stmts)
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'text'}}],
                  'indexes': {'t1_idx': {'keys': [
                      {'lower(c2)': {'type': 'expression'}}]}}}
        assert dbmap['schema public']['table t1'] == expmap

    def test_index_function_complex(self):
        "Map indexes using nested functions and complex arguments"
        stmts = ["CREATE TABLE t1 (c1 integer, c2 text, c3 date)",
                 "CREATE INDEX t1_idx1 ON t1 (substring(c2 from position("
                 "'_begin' in c2)), substring(c2 from position('_end' in "
                 "c2)))",
                 "CREATE INDEX t1_idx2 ON t1 (extract(month from c3), "
                 "extract(day from c3))"]
        dbmap = self.to_map(stmts)
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'text'}},
                              {'c3': {'type': 'date'}}],
                  'indexes': {'t1_idx1': {
                      'keys': [{'"substring"(c2, "position"(c2, \'_begin\''
                                '::text))': {'type': 'expression'}},
                               {'"substring"(c2, "position"(c2, \'_end\''
                                '::text))': {'type': 'expression'}}]},
                              't1_idx2': {
                      'keys': [{"date_part('month'::text, c3)": {
                                'type': 'expression'}},
                               {"date_part('day'::text, c3)": {
                                'type': 'expression'}}]}}}
        assert dbmap['schema public']['table t1'] == expmap

    def test_index_col_opts(self):
        "Map an index with various column options"
        stmts = ["CREATE TABLE t1 (c1 cidr, c2 text)",
                 "CREATE INDEX t1_idx ON t1 (c1 cidr_ops NULLS FIRST, "
                 "c2 DESC)"]
        dbmap = self.to_map(stmts)
        expmap = {'columns': [{'c1': {'type': 'cidr'}},
                              {'c2': {'type': 'text'}}],
                  'indexes': {'t1_idx': {'keys': [
                      {'c1': {'opclass': 'cidr_ops', 'nulls': 'first'}},
                      {'c2': {'order': 'desc'}}]}}}
        assert dbmap['schema public']['table t1'] == expmap

    def test_index_mixed(self):
        "Map indexes using functions, a regular column and expressions"
        stmts = ["CREATE TABLE t1 (c1 integer, c2 text, c3 text)",
                 "CREATE INDEX t1_idx ON t1 (btrim(c3, 'x') NULLS FIRST, c1, "
                 "lower(c2) DESC)",
                 "CREATE INDEX t1_idx2 ON t1 ((c2 || ', ' || c3), "
                 "(c3 || ' ' || c2))"]
        dbmap = self.to_map(stmts)
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'text'}},
                              {'c3': {'type': 'text'}}],
                  'indexes': {'t1_idx': {
                      'keys': [{"btrim(c3, 'x'::text)": {
                                'type': 'expression', 'nulls': 'first'}},
                               'c1', {'lower(c2)': {
                                   'type': 'expression', 'order': 'desc'}}]},
                              't1_idx2': {
                      'keys': [{"(((c2 || ', '::text) || c3))": {
                                'type': 'expression'}},
                               {"(((c3 || ' '::text) || c2))": {
                                'type': 'expression'}}]}}}
        assert dbmap['schema public']['table t1'] == expmap

    def test_map_index_cluster(self):
        "Map a table with an index and cluster on it"
        dbmap = self.to_map([CREATE_TABLE_STMT, CREATE_STMT,
                             "CLUSTER t1 USING t1_idx"])
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'text'}}],
                  'indexes': {'t1_idx': {'keys': ['c1'], 'cluster': True}}}
        assert dbmap['schema public']['table t1'] == expmap

    def test_map_index_comment(self):
        "Map an index comment"
        dbmap = self.to_map([CREATE_TABLE_STMT, CREATE_STMT, COMMENT_STMT])
        assert dbmap['schema public']['table t1']['indexes']['t1_idx'][
            'description'] == 'Test index t1_idx'

    def test_bug_98(self):
        "Map a multicol index with expressions"
        dbmap = self.to_map(["CREATE TABLE holiday (id serial PRIMARY KEY,"
                             "date date NOT NULL, recurring boolean NOT NULL)",
                             "CREATE UNIQUE INDEX unique_date ON holiday (("
                             "CASE WHEN recurring THEN (0)::double precision "
                             "ELSE date_part('year'::text, date) END), "
                             "date_part('month'::text, date), "
                             "date_part('day'::text, date))"])
        fmt = "(\nCASE\n    %s\n    %s\nEND)"
        if self.db.version < 90300:
            fmt = "(CASE %s %s END)"
        assert dbmap['schema public']['table holiday']['indexes'][
            'unique_date'] == {
                'keys': [
                {fmt % ("WHEN recurring THEN (0)::double precision",
                        "ELSE date_part('year'::text, date)"):
                {'type': 'expression'}},
                {"date_part('month'::text, date)": {'type': 'expression'}},
                {"date_part('day'::text, date)": {'type': 'expression'}}],
                'unique': True}


class IndexToSqlTestCase(InputMapToSqlTestCase):
    """Test SQL generation from input indexes"""

    def test_create_table_with_index(self):
        "Create new table with a single column index"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': ['c1']}}}})
        sql = self.to_sql(inmap)
        assert fix_indent(sql[0]) == "CREATE TABLE t1 (c1 integer, c2 text)"
        assert sql[1] == "CREATE INDEX t1_idx ON t1 (c1)"

    def test_add_index(self):
        "Add a two-column unique index to an existing table"
        stmts = ["CREATE TABLE t1 (c1 INTEGER NOT NULL, "
                 "c2 INTEGER NOT NULL, c3 TEXT)"]
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer', 'not_null': True}},
                        {'c2': {'type': 'integer', 'not_null': True}},
                        {'c3': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': ['c2', 'c1'], 'unique': True}}}})
        sql = self.to_sql(inmap, stmts)
        assert sql == ["CREATE UNIQUE INDEX t1_idx ON t1 (c2, c1)"]

    def test_add_index_schema(self):
        "Add an index to an existing table in a non-public schema"
        stmts = ["CREATE SCHEMA s1",
                 "CREATE TABLE s1.t1 (c1 INTEGER NOT NULL, "
                 "c2 INTEGER NOT NULL, c3 TEXT)"]
        inmap = self.std_map()
        inmap.update({'schema s1': {'table t1': {
            'columns': [{'c1': {'type': 'integer', 'not_null': True}},
                        {'c2': {'type': 'integer', 'not_null': True}},
                        {'c3': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': ['c2', 'c1'], 'unique': True}}}}})
        sql = self.to_sql(inmap, stmts)
        assert sql == ["CREATE UNIQUE INDEX t1_idx ON s1.t1 (c2, c1)"]

    def test_add_index_back_compat(self):
        "Add a index to an existing table accepting back-compatible spec"
        stmts = ["CREATE TABLE t1 (c1 INTEGER NOT NULL, "
                 "c2 INTEGER NOT NULL, c3 TEXT)"]
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer', 'not_null': True}},
                        {'c2': {'type': 'integer', 'not_null': True}},
                        {'c3': {'type': 'text'}}],
            'indexes': {'t1_idx': {'columns': ['c2', 'c1'], 'unique': True,
                                   'access_method': 'btree'}}}})
        sql = self.to_sql(inmap, stmts)
        assert sql == ["CREATE UNIQUE INDEX t1_idx ON t1 (c2, c1)"]

    def test_bad_index(self):
        "Fail on creating an index without columns or expression"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}}, {'c2': {'type': 'text'}}],
            'indexes': {'t1_idx': {'access_method': 'btree'}}}})
        with pytest.raises(KeyError):
            self.to_sql(inmap)

    def test_create_partial(self):
        "Create a partial index"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': ['c2'],
                                   'predicate': '(c1 > 42)'}}}})
        sql = self.to_sql(inmap, [CREATE_TABLE_STMT])
        assert fix_indent(sql[0]) == \
            "CREATE INDEX t1_idx ON t1 (c2) WHERE (c1 > 42)"

    def test_create_index_function(self):
        "Create an index which uses a function"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}}, {'c2': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': [{
                'lower(c2)': {'type': 'expression'}}]}}}})
        sql = self.to_sql(inmap)
        assert sql[1] == "CREATE INDEX t1_idx ON t1 (lower(c2))"

    def test_create_index_col_opts(self):
        "Create table and an index with column options"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'cidr'}}, {'c2': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': [{'c1': {
                'opclass': 'cidr_ops', 'nulls': 'first'}}, 'c2']}}}})
        sql = self.to_sql(inmap)
        assert sql[1] == "CREATE INDEX t1_idx ON t1 " \
            "(c1 cidr_ops NULLS FIRST, c2)"

    def test_index_mixed(self):
        "Create indexes using functions, a regular column and expressions"
        stmts = ["CREATE TABLE t1 (c1 integer, c2 text, c3 text)"]
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}}, {'c2': {'type': 'text'}},
                        {'c3': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': [
                {"btrim(c3, 'x'::text)": {'type': 'expression',
                                          'nulls': 'first'}}, 'c1',
                {'lower(c2)': {'type': 'expression', 'order': 'desc'}}]},
                't1_idx2': {'keys': [
                    {"(((c2 || ', '::text) || c3))": {'type': 'expression'}},
                    {"(((c3 || ' '::text) || c2))": {
                        'type': 'expression'}}]}}}})
        sql = sorted(self.to_sql(inmap, stmts))
        assert sql[0] == "CREATE INDEX t1_idx ON t1 (" \
            "btrim(c3, 'x'::text) NULLS FIRST, c1, lower(c2) DESC)"
        assert sql[1] == "CREATE INDEX t1_idx2 ON t1 (" \
            "(((c2 || ', '::text) || c3)), (((c3 || ' '::text) || c2)))"

    def test_create_table_with_index_clustered(self):
        "Create new table clustered on a single column index"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': ['c1'], 'cluster': True}}}})
        sql = self.to_sql(inmap)
        assert sql[2] == "CLUSTER t1 USING t1_idx"

    def test_cluster_table_with_index(self):
        "Change a table with an index to cluster on it"
        stmts = [CREATE_TABLE_STMT, CREATE_STMT]
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}}, {'c2': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': ['c1'], 'cluster': True}}}})
        sql = self.to_sql(inmap, stmts)
        assert sql[0] == "CLUSTER t1 USING t1_idx"

    def test_uncluster_table_with_index(self):
        "Change a table clustered on an index to remove cluster"
        stmts = [CREATE_TABLE_STMT, CREATE_STMT, "CLUSTER t1 USING t1_idx"]
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}}, {'c2': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': ['c1']}}}})
        sql = self.to_sql(inmap, stmts)
        assert fix_indent(sql[0]) == "ALTER TABLE t1 SET WITHOUT CLUSTER"

    def test_comment_on_index(self):
        "Create a comment for an existing index"
        stmts = [CREATE_TABLE_STMT, CREATE_STMT]
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}}, {'c2': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': ['c1'],
                                   'description': 'Test index t1_idx'}}}})
        sql = self.to_sql(inmap, stmts)
        assert sql == [COMMENT_STMT]

    def test_drop_index_comment(self):
        "Drop the comment on an existing index"
        stmts = [CREATE_TABLE_STMT, CREATE_STMT, COMMENT_STMT]
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}}, {'c2': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': ['c1']}}}})
        sql = self.to_sql(inmap, stmts)
        assert sql == ["COMMENT ON INDEX t1_idx IS NULL"]

    def test_change_index_comment(self):
        "Change existing comment on an index"
        stmts = [CREATE_TABLE_STMT, CREATE_STMT, COMMENT_STMT]
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}}, {'c2': {'type': 'text'}}],
            'indexes': {'t1_idx': {'keys': ['c1'],
                                   'description': 'Changed index t1_idx'}}}})
        sql = self.to_sql(inmap, stmts)
        assert sql == ["COMMENT ON INDEX t1_idx IS 'Changed index t1_idx'"]
