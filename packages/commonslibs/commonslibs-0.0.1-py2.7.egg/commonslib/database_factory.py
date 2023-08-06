#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2011-6-13
A lightweight wrapper around MySQLdb.
author: huwei
"""
import copy
import MySQLdb.constants
import MySQLdb.converters
import MySQLdb.cursors
import itertools
import logging
import time
import re
import yaml
import os.path
from configs.settings import Settings
from MySQLdb.cursors import CursorStoreResultMixIn, CursorTupleRowsMixIn


class BaseCursor(MySQLdb.cursors.BaseCursor):

    @staticmethod
    def _get_query_parameters(query, params):
        if isinstance(params, dict) and params:
            p = re.compile(':\w+')
            result_param = [params.get(param_token[1:], None) for param_token in p.findall(query)]
            return p.sub('%s', query), result_param
        elif isinstance(params, list) and params:
            return query.replace('?', '%s'), params
        elif params is None:
            return query
        else:
            return query.replace('?', '%s'), [params]

    def execute(self, query, args=None):
        if args:
            query, params = self._get_query_parameters(query, args)
            return MySQLdb.cursors.BaseCursor.execute(self, query, params)
        else:
            return MySQLdb.cursors.BaseCursor.execute(self, query)


class Cursor(CursorStoreResultMixIn, CursorTupleRowsMixIn,
             BaseCursor):
    """This is the standard Cursor class that returns rows as tuples
    and stores the result set in the client."""


class DataBaseFactory(object):
    """A lightweight wrapper around MySQLdb DB-API connections.

    The main value we provide is wrapping rows in a dict/object so that
    columns can be accessed by name. Typical usage::

        db = database.Connection("localhost", "mydatabase")
        for article in db.gets("SELECT * FROM articles"):
            print article.title

    Cursors are hidden by the implementation, but other than that, the methods
    are very similar to the DB-API.

    We explicitly set the timezone to UTC and the character encoding to
    UTF-8 on all connections to avoid time zone and encoding errors.
    """
    databases_config = None

    @staticmethod
    def get_instance(name, runmod='development'):
        if not DataBaseFactory.databases_config:
            file_stream = file(os.path.join(Settings.SITE_ROOT_PATH, 'configs/databases.yaml'), 'r')
            yml = yaml.load(file_stream)
            # if options.runmod is None:
            #     options.runmod = 'development'
            # if options.get('runmod') is None:
            #     options.runmod='development'
            DataBaseFactory.databases_config = yml.get(runmod)
        database_config = DataBaseFactory.databases_config.get(name)
        if database_config:
            return DataBaseFactory(database_config.get('host'),
                                   database_config.get('database'),
                                   user=database_config.get('username'),
                                   password=database_config.get('password'),
                                   charset=database_config.get('encoding'))
        else:
            return None

    def __init__(self, host, database, user=None, password=None, charset="utf8",
                 max_idle_time=7 * 3600):
        self.host = host
        self.database = database
        self.max_idle_time = max_idle_time

        args = dict(conv=CONVERSIONS, use_unicode=True, charset=charset,
                    db=database, sql_mode="TRADITIONAL")
        if user is not None:
            args["user"] = user
        if password is not None:
            args["passwd"] = password

        # We accept a path to a MySQL socket file or a host(:port) string
        if "/" in host:
            args["unix_socket"] = host
        else:
            self.socket = None
            pair = host.split(":")
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = 3306

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except:
            logging.error("Cannot connect to MySQL on %s", self.host,
                          exc_info=True)

    def __del__(self):
        self.close()

    def _ensure_connected(self):
        # Mysql by default closes client connections that are idle for
        # 8 hours, but the client library does not report this fact until
        # you try to perform a gets and it fails.  Protect against this
        # case by preemptively closing and reopening the connection
        # if it has been idle for too long (7 hours by default).
        if (self._db is None or
                (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return Cursor(self._db)

    @staticmethod
    def _close_cursor(cursor):
        cursor.close()

    def begin_transaction(self):
        pass

    def commit(self):
        if getattr(self, "_db", None) is not None:
            self._db.commit()

    def rollback(self):
        if getattr(self, "_db", None) is not None:
            self._db.rollback()

    def _execute(self, cursor, query, parameters):
        try:
            return cursor.execute(query, parameters)
        except OperationalError:
            logging.error("Error connecting to MySQL on %s", self.host)
            self.close()
            raise

    @staticmethod
    def _get_union_query(query, count):
        union_query = ''
        for i in range(count):
            union_query += query
            if i < count - 1:
                union_query += " UNION ALL "
        return union_query

    def _get_union_query_params(self, query, params):
        """get union query and params.
        #TODO:存在问题，如果需要传入两个参数，那么这个算法将会失败
            [('select * from ab where id=? union all select * from ab where id=?', [1,2])]
        :param query:
        :param params:
        """
        union_count = int(30)
        params_count = len(params)
        left_counts = params_count % union_count
        if left_counts > 0:
            full_counts = int(params_count / union_count) + 1
        else:
            full_counts = int(params_count / union_count)
        union_query_params = []
        for i in range(full_counts):
            start = i * union_count
            end = min((i + 1) * union_count, params_count)
            if end == params_count and left_counts > 0:
                union_query = self._get_union_query(query, left_counts)
            else:
                union_query = self._get_union_query(query, union_count)
            sub_params = params[start:end]
            if sub_params:
                union_query_params.append((union_query, params[start:end]))
        return union_query_params

    def gets_by_ids(self, query, params):
        union_query_params = self._get_union_query_params(query, params)
        results = []
        if union_query_params:
            for i in range(len(union_query_params)):
                (union_query, sub_params) = union_query_params[i]
                results += self.gets(union_query, sub_params)
        return results

    def get_dict_by_ids(self, query, params):
        if isinstance(params, list):
            parameters = set(params)
        else:
            parameters = params
        results = dict()
        if parameters:
            for param in parameters:
                results[param] = self.get(query, param)
        return results

    def close(self):
        """Closes this database connection."""
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = MySQLdb.connect(**self._db_args)
        self._db.autocommit(True)

    def iter(self, query, *parameters):
        """Returns an iterator for the given gets and parameters."""
        self._ensure_connected()
        cursor = MySQLdb.cursors.SSCursor(self._db)
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            for row in cursor:
                yield Row(zip(column_names, row))
        finally:
            cursor.close()

    def gets(self, query, params=None, offset=None, count=None):
        """Returns a row list for the given gets and params.
        example:
        ::

            gets('select * from roles where user_id=:user_id and name=:name', dict(user_id=1,name='abc'))
            gets('select * from roles where user_id=? and name=?', [1, 'abc'], offset=0, count=15)
            gets('select * from roles where user_id=%s and name=%s', [1, 'abc'])
        """
        if (offset is not None) and (count is not None):
            query += ' limit ' + str(offset) + ',' + str(count)
        cursor = self._cursor()
        try:
            self._execute(cursor, query, params)
            column_names = [d[0] for d in cursor.description]
            return [Row(itertools.izip(column_names, row)) for row in cursor]
        finally:
            self._close_cursor(cursor)

    def get_one(self, query, params=None):
        """Returns the first row first field returned for the given query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, params)
            data = cursor.fetchone()
            if data is None:
                return None
            return data[0]
        finally:
            self._close_cursor(cursor)

    def get(self, query, params=None):
        """Returns the first row returned for the given query."""
        rows = self.gets(query, params)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned for Database.get() getsquery")
        else:
            return rows[0]

    def execute(self, query, params=None):
        """Executes the given gets, returning the lastrowid from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, params)
            return cursor.lastrowid
        finally:
            self._close_cursor(cursor)

    def executemany(self, query, parameters):
        """Executes the given gets against all the given param sequences.
        We return the lastrowid from the gets.
        example:
        ::
            db.executemany(
              'INSERT INTO breakfast (name, spam, eggs, sausage, price)
              VALUES (%s, %s, %s, %s, %s)',
              [
              ("Spam and Sausage Lover's Plate", 5, 1, 8, 7.95 ),
              ("Not So Much Spam Plate", 3, 2, 0, 3.95 ),
              ("Don't Wany ANY SPAM! Plate", 0, 4, 3, 5.95 )
              ] )
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()


class Row(dict):
    """A dict that allows for object-like property access syntax."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def __setattr__(self, *args, **kwargs):
        if args and len(args) == 2:
            self[args[0]] = args[1]
        else:
            return dict.__setattr__(self, *args, **kwargs)

# Fix the access conversions to properly recognize unicode/binary
FIELD_TYPE = MySQLdb.constants.FIELD_TYPE
FLAG = MySQLdb.constants.FLAG
CONVERSIONS = copy.deepcopy(MySQLdb.converters.conversions)

field_types = [FIELD_TYPE.BLOB, FIELD_TYPE.STRING, FIELD_TYPE.VAR_STRING]
if 'VARCHAR' in vars(FIELD_TYPE):
    field_types.append(FIELD_TYPE.VARCHAR)

for field_type in field_types:
    CONVERSIONS[field_type].insert(0, (FLAG.BINARY, str))


# Alias some common MySQL exceptions
IntegrityError = MySQLdb.IntegrityError
OperationalError = MySQLdb.OperationalError

if __name__ == "__main__":
    print [1, 2, 3, 2, 4] + [1232, 123, 123, 123]
    db = DataBaseFactory.get_instance(u'default')
    #print db.gets_by_ids(u'select * from users where id=?', range(31))
    print db.get_dict_by_ids(u'select * from users where id=?', [1, 1, 1, 2, 2, 2, 3, 3, 3])

