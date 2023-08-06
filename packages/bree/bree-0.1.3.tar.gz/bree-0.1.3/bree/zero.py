# -*- coding: utf-8 -*-



from tornado.testing import gen_test

from tornado.ioloop import IOLoop, TimeoutError
from tornado.gen import coroutine

import types
import functools


class ZeroCache:
    zero_generator = None

    pass


def zero(func=None, timeout=float(5)):
    """
    init for async code
    """

    def wrap(f):
        @functools.wraps(f)
        def pre_coroutine(self, *args, **kwargs):
            result = f(self, *args, **kwargs)
            if isinstance(result, types.GeneratorType):
                ZeroCache.zero_generator = result
            else:
                ZeroCache.zero_generator = None
            return result

        coro = coroutine(pre_coroutine)

        @functools.wraps(coro)
        def post_coroutine(self, *args, **kwargs):
            try:
                return IOLoop.instance().run_sync(
                    functools.partial(coro, self, *args, **kwargs),
                    timeout=timeout)
            except TimeoutError as e:
                # run_sync raises an error with an unhelpful traceback.
                # If we throw it back into the generator the stack trace
                # will be replaced by the point where the test is stopped.
                ZeroCache.zero_generator.throw(e)
                # In case the test contains an overly broad except clause,
                # we may get back here.  In this case re-raise the original
                # exception, which is better than nothing.
                raise

        return post_coroutine

    if func is not None:
        # Used like:
        # @gen_test
        #     def f(self):
        #         pass
        return wrap(func)
    else:
        # Used like @gen_test(timeout=10)
        return wrap


