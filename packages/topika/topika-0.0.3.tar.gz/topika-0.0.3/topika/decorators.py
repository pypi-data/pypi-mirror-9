#!/usr/bin/env python
# encoding: utf-8
import tornado.ioloop
from tornado.log import app_log as log
from tornado.gen import Future
from heapq import heappush
from functools import wraps, partial


def queued(order=1000):
    def deco(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            f = Future()
            def run():
                try:
                    f.set_result(func(self, *args, **kwargs))
                except Exception as e:
                    f.set_exception(e)

            if self.channel and self.channel.is_open:
                log.debug("Running %r", func)
                tornado.ioloop.IOLoop.instance().add_callback(run)
            else:
                log.debug("Queued %r", func)
                heappush(self._queue, (order, run))

            return f
        return wrap
    return deco


def memory(order=1000):
    def deco(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            heappush(self._memory, (order, partial(func, self, *args, **kwargs)))
            return func(self, *args, **kwargs)

        return wrap
    return deco
