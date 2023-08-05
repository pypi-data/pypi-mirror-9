#coding:utf8

"""
Created on 2014-05-19

@author: tufei
@description: 基于tornado的异步数据库模块（目前仅支持mysql）
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
import MySQLdb
import tornado.concurrent
import tornado.gen
import tornado.stack_context
from tornado.ioloop import IOLoop
from DBUtils.PooledDB import PooledDB
from dhkit import log
from dhkit.threadpool import ThreadPool, Result
from functools import partial, wraps
from collections import OrderedDict


class DatabaseError(Exception):
    """数据库访问异常
    """


class TransactionError(DatabaseError):
    """数据库事务异常
    """


class ConnectionFactory(object):
    """
    """
    _connection_pool = None
    _thread_pool = None
    _io_loop = None

    @classmethod
    def initialize(cls, creater=MySQLdb, row_mapper_cls=None, num_threads=16, ioloop=None, **kwargs):
        cls._connection_pool = PooledDB(creater, **kwargs)
        cls._io_loop = ioloop or IOLoop.current()
        DatabaseTemplate.ROWMAPPER_CLS = row_mapper_cls or DictionaryRowMapper
        cls._thread_pool = ThreadPool(ioloop=cls._io_loop, num_threads=num_threads)

    @classmethod
    def get_db(cls):
        return DatabaseTemplate(cls._connection_pool, cls._thread_pool, cls._io_loop)

    @classmethod
    def destroy(cls):
        cls._thread_pool.stop()


class MetaData(OrderedDict):

    def __init__(self, desc_row):
        super(MetaData, self).__init__()
        self['name'] = desc_row[0]
        self['type_code'] = desc_row[1]
        self['display_size'] = desc_row[2]
        self['internal_size'] = desc_row[3]
        self['precision'] = desc_row[4]
        self['scale'] = desc_row[5]
        self['null_ok'] = desc_row[6]

    def __getitem__(self, key):
        try:
            return super(MetaData, self).__getitem__(key)
        except KeyError:
            if isinstance(key, int):
                name, value = self.items()[key]
                return value
            else:
                raise
        except TypeError:
            if isinstance(key, slice):
                items = self.items()[key]
                values = []
                for name, value in items:
                    values.append(value)
                return tuple(values)
            else:
                raise


class RowMapper(object):
    """
    This is an interface to handle one row of data.
    """
    def map_row(self, row, metadata):
        raise NotImplementedError()


class DictionaryRowMapper(RowMapper):
    """
    This row mapper converts the tuple into a dictionary using the column names as the keys.
    """
    def map_row(self, row, metadata):
        obj = {}
        for i, column in enumerate(metadata):
            obj[column["name"]] = row[i]
        return obj


class SimpleRowMapper(RowMapper):
    """
    This row mapper uses convention over configuration to create and populate attributes
    of an object.
    """
    def __init__(self, clazz):
        self.clazz = clazz

    def map_row(self, row, metadata):
        obj = self.clazz()
        for i, column in enumerate(metadata):
            setattr(obj, column["name"], row[i])
        return obj


def async(func):
    @wraps(func)
    def decorator(self, *args, **kwargs):
        callback = kwargs.get('callback')
        future = tornado.concurrent.Future()
        if callback is not None:
            callback = tornado.stack_context.wrap(callback)

            def handle_future(_future):
                exc = _future.exception()
                if exc is not None and exc.response is not None:
                    response = exc.response
                else:
                    response = _future.result()
                self.ioloop.add_callback(callback, response)
            future.add_done_callback(handle_future)

        def handle_result(result):
            error = result.get_error()
            if error:
                future.set_exception(error)
            else:
                future.set_result(result.get_result())

        kwargs['callback'] = handle_result
        func(self, *args, **kwargs)
        return future
    return decorator


class DatabaseTemplate(object):

    ROWMAPPER_CLS = DictionaryRowMapper

    def __init__(self, connection_pool, threadpool, ioloop=None):
        self.connection_pool = connection_pool
        self.ioloop = ioloop or IOLoop.instance()
        self.threadpool = threadpool

    def _execute(self, sql_statement, params=None, conn=None):
        if conn is None:
            in_transaction = False
            conn = self.connection_pool.connection()
        else:
            in_transaction = True
        cursor = conn.cursor()
        try:
            log.debug("sql:[%s], params:[%s]" % (sql_statement, params))
            if params:
                cursor.execute(sql_statement, params)
            else:
                cursor.execute(sql_statement)
            rowcount = cursor.rowcount
            lastrowid = cursor.lastrowid
            if not in_transaction:
                conn.commit()
            return [rowcount, lastrowid]
        except Exception, e:
            log.exception("database execute error. sql:[%s], params:[%s]" % (sql_statement, params))
            if not in_transaction:
                conn.rollback()
            raise DatabaseError(self.fomat_exc(e))
        finally:
            try:
                cursor.close()
                if not in_transaction:
                    conn.close()
            except Exception, e:
                log.debug("release database connction error: %s" % e.message)

    @async
    def begin(self, callback=None):
        conn = self.connection_pool.connection()
        log.debug('begin transaction ... connection:[%s]' % conn)
        callback(Result(conn))

    @async
    def commit(self, conn, callback=None):
        self.threadpool.add_task(partial(self._commit, conn), callback)

    def _commit(self, conn):
        log.debug('commit transaction ... connection:[%s]' % conn)
        conn.commit()
        conn.close()

    @async
    def rollback(self, conn, callback=None):
        self.threadpool.add_task(partial(self._rollback, conn), callback)

    def _rollback(self, conn):
        log.debug('rollback transaction ... connection:[%s]' % conn)
        conn.rollback()
        conn.close()

    @async
    def execute(self, sql_statement, params=None, conn=None, callback=None):
        self.threadpool.add_task(partial(self._execute, sql_statement, params, conn), callback)

    @tornado.gen.coroutine
    def insert(self, sql_statement, params=None, conn=None):
        rv = yield self.execute(sql_statement, params, conn)
        raise tornado.gen.Return(rv[1])

    @tornado.gen.coroutine
    def update(self, sql_statement, params=None, conn=None):
        rv = yield self.execute(sql_statement, params, conn)
        raise tornado.gen.Return(rv[0])

    def _query(self, sql_statement, params=None, conn=None, return_metadata=False, row_mapper=None):
        if conn is None:
            in_transaction = False
            conn = self.connection_pool.connection()
        else:
            in_transaction = True
        cursor = conn.cursor()
        try:
            log.debug("sql:[%s], params:[%s]" % (sql_statement, params))
            if params:
                cursor.execute(sql_statement, params)
            else:
                cursor.execute(sql_statement)
            rs = cursor.fetchall()
            metadata = [MetaData(desc_row) for desc_row in cursor.description]
            if rs:
                if not row_mapper:
                    row_mapper = self.ROWMAPPER_CLS()
                result = [row_mapper.map_row(row, metadata) for row in rs]
            else:
                result = []
            if return_metadata:
                return result, metadata
            else:
                return result
        except Exception, e:
            log.exception("database query error. sql:[%s], params:[%s]" % (sql_statement, params))
            raise DatabaseError(self.fomat_exc(e))
        finally:
            try:
                cursor.close()
                if not in_transaction:
                    conn.close()
            except Exception, e:
                log.debug("release database connection error: %s" % e.message)

    @async
    def query(self, sql_statement, params=None, conn=None, return_metadata=False, row_mapper=None, callback=None):
        self.threadpool.add_task(
            partial(self._query, sql_statement, params, conn, return_metadata, row_mapper), callback)

    @tornado.gen.coroutine
    def get(self, sql_statement, params=None, conn=None, return_metadata=False, row_mapper=None):
        rs = yield self.query(sql_statement, params, conn, return_metadata, row_mapper)
        raise tornado.gen.Return(rs[0] if rs else None)

    def fomat_exc(self, exc):
        if isinstance(exc, MySQLdb.Error):
            return "MySQLdb Error %d: %s" % (exc.args[0], exc.args[1])
        return exc.message