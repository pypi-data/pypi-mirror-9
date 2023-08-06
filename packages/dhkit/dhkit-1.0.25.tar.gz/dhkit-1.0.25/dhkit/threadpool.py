# coding:utf8

"""
Created on 2014-12-01

@author: tufei
@description: 基于tornado IOLoop的线程池
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
from threading import Thread
from tornado.ioloop import IOLoop
from tornado.concurrent import TracebackFuture
from Queue import Queue, Empty
from functools import partial
from dhkit import log


class ThreadPool(object):

    def __init__(self, num_threads=5, queue_timeout=0.1, ioloop=None):
        self._num_threads = num_threads
        self._queue = Queue()
        self._queue_timeout = queue_timeout
        self._threads = []
        self.ioloop = ioloop or IOLoop.instance()
        self.running = True
        for i in xrange(self._num_threads):
            thd = ThreadWorker(self)
            self._threads.append(thd)
            thd.start()

    def get_task(self):
        return self._queue.get(True, self._queue_timeout)

    def add_task(self, func, callback):
        self._queue.put((func, callback))

    def stop(self):
        self.running = False
        for thd in self._threads:
            thd.join()


class Result(object):

    def __init__(self, result=None, error=None):
        self._result = result
        self._error = error

    def get_result(self):
        return self._result

    def get_error(self):
        return self._error


class ThreadWorker(Thread):

    def __init__(self, pool):
        self._pool = pool
        super(ThreadWorker, self).__init__()

    def run(self):
        while self._pool.running:
            func, callback = None, None
            try:
                func, callback = self._pool.get_task()
                result = func()
                if callback:
                    self._pool.ioloop.add_callback(partial(callback, Result(result)))
            except Empty:
                pass
            except Exception, ex:
                log.exception('run function: %s error' % func)
                if callback:
                    self._pool.ioloop.add_callback(partial(callback, Result(error=ex)))