import logging
import time
from functools import wraps

from . import compat

compat.patch()  # monkey-patch time.perf_counter

log = logging.getLogger('amqpy')


def synchronized(lock_name):
    """Decorator for automatically acquiring and releasing lock for method call

    This decorator accesses the `lock_name` :class:`threading.Lock` attribute of the instance that
    the wrapped method is bound to. The lock is acquired (blocks indefinitely) before the method is
    called. After the method has executed, the lock is released.

    Decorated methods should not be long-running operations, since the lock is held for the duration
    of the method's execution.

    :param lock_name: name of :class:`threading.Lock` object
    """

    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            lock = getattr(self, lock_name)
            acquired = lock.acquire(False)
            if not acquired:
                # log.debug('> Wait to acquire lock for [{}]'.format(f.__qualname__))
                start_time = time.perf_counter()
                lock.acquire()
                tot_time = time.perf_counter() - start_time
                if tot_time > 10:
                    # only log if waited for more than 10s to acquire lock
                    log.debug('Acquired lock for [{}] in: {:.3f}s'.format(f.__qualname__, tot_time))
            try:
                retval = f(self, *args, **kwargs)
            finally:
                lock.release()
            return retval

        return wrapper

    return decorator
