'''logged decorator module'''
import logging
from functools import wraps
from traceback import extract_stack
from textwrap import wrap
logger = logging.getLogger(__name__)

def logged(logger=logger, level=logging.DEBUG):
    '''the logged decorator'''
    def decorator_wrapper(fn):
        @wraps(fn)
        def wrapper(*args, **kvs):
            ret = None
            if logger.isEnabledFor(level):
                # performance reasons
                # not indent logged, decorator_wrapper, wraps & wrapper
                indent = len(extract_stack()) - 4
                assert indent > 0, 'oOops'
                call_str = '-> %s(*%s, **%s)' % (fn.__name__, args, kvs) 
                for log_line in wrap(call_str, initial_indent=' ' * indent,
                                        subsequent_indent=' ' * indent):
                    logger.log(level, log_line)
                try:
                    ret = fn(*args, **kvs)
                finally:
                    ret_str = '<- %s' % (ret,)
                    for log_line in wrap(ret_str, initial_indent=' ' * indent,
                                            subsequent_indent=' ' * indent):
                        logger.log(level, log_line)
            else:
                # logging not enabled, no need to try:...
                ret = fn(*args, **kvs)
            return ret
        return wrapper
    return decorator_wrapper

__all__ = ['logged']

                
