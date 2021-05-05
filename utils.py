import logging

from threading import RLock
from datetime import datetime, timedelta
from functools import update_wrapper


class TimedLruCache:
    """
    decorator that caches a function's return value each time it is called
    cache is automatically invalidated after given expiration time
    """

    def __init__(self, expiration=timedelta.max, typed=True):
        """
        :param expiration: timedelta object
        :param typed: treat function calls with different arguments as distinct
        """
        self.expiration = expiration
        self.typed = typed
        self.cache = {}
        self.cache_lock = RLock()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.func = None
        self.do_not_cache = False

    def __call__(self, func):
        def timed_lru_cache_impl(*args, **kwargs):
            call_args = self._concat_args(*args, **kwargs)
            call_repr = self._get_call_repr(*args, **kwargs)
            now = datetime.now()

            try:
                hash(call_args)
            except TypeError:
                self.logger.warning(f'not hashable: {call_repr}')
                return func(*args, **kwargs)

            with self.cache_lock:
                if call_args in self.cache and (now - self.cache[call_args][1] > self.expiration):
                    self.logger.debug(f'cache expired: {call_repr}')
                    del self.cache[call_args]

                if call_args not in self.cache:
                    try:
                        func_result = func(*args, **kwargs)
                        if self.do_not_cache:
                            self.do_not_cache = False
                            self.logger.debug(f'not cached on demand: {call_repr}')
                        else:
                            self.cache[call_args] = (func_result, now)
                            self.logger.debug(f'cached function result: {call_repr} -> {func_result}')

                        return func_result

                    except Exception as e:
                        self.logger.info(f'exception caught calling: {call_repr}, no result cached: {type(e).__name__}: {e}')
                        raise e from None
                else:
                    self.logger.debug(f'returned cached result: {call_repr} -> {self.cache[call_args][0]}')
                    return self.cache[call_args][0]

        self.func = func
        func.clear_cache = self._clear_cache
        func.do_not_cache = self._do_not_cache
        return update_wrapper(timed_lru_cache_impl, func)

    def _concat_args(self, *args, **kwargs):
        if self.typed:
            result = args
            if kwargs: result += (self.__magic_separator,) + tuple(sorted(kwargs.items()))
            return result

        return None

    def _get_call_repr(self, *args, **kwargs):
        return f'{self.func.__qualname__}({", ".join([repr(x) for x in args] + [str(k) + "=" + repr(v) for k, v in kwargs.items()])})'

    class __magic_separator: pass

    def _clear_cache(self):
        with self.cache_lock:
            self.cache = {}

        self.logger.debug(f'cache cleared: {self.func.__qualname__}')

    def _do_not_cache(self):
        with self.cache_lock:
            self.do_not_cache = True