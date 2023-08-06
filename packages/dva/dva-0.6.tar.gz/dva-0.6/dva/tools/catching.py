'''
catching decorator module
'''
import sys
import functools
import logging
logger = logging.getLogger(__name__)



def catching(logger=logger, level=logging.ERROR):
    '''decorating in try/exept&log err'''
    def dercorator_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kvs):
            try:
                ret = func(*args, **kvs)
            except exception as err:
                logger.log(level, '%s failed: %s', func.__name__, err)
                sys.exit(2)
            return ret
        return wrapper
    return decorator_wrapper
