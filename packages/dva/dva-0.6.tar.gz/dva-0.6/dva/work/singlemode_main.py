'''
basic serial main function module
'''

import time
import logging
import traceback
from data import load, save_result, strip_ephemeral
from contextlib import contextmanager
from stage import assert_image, create_instance, attempt_ssh, allow_root_login, \
        global_setup_script, terminate_instance, SkipError, StageError
from test import test_execute
from common import RESULT_ERROR

logger = logging.getLogger(__name__)

class ProgressInfo(object):
    def __init__(self, params):
        self.total = 0
        self.processed = 0
        from gevent.coros import RLock
        self.lock = RLock()
        for item in params:
            for test_stage in item['test_stages']:
                for test_name in item['test_stages'][test_stage]:
                    self.total += 1

    def __str__(self):
        return '# %s %2.2f%% (%s/%s)' % (time.ctime(), self.total and float((self.processed* 100)/self.total) or 0, self.processed, self.total)

    def incr(self):
        with self.lock:
            self.processed += 1

@contextmanager
def image_ctx(params):
    yield assert_image(params)

@contextmanager
def instance_ctx(params):
    with image_ctx(params) as params:
        params = create_instance(params)
        try:
            yield params
        finally:
            terminate_instance(params)

@contextmanager
def ssh_ctx(params):
    with instance_ctx(params) as params:
        yield attempt_ssh(params)

@contextmanager
def root_ctx(params):
    with ssh_ctx(params) as params:
        yield allow_root_login(params)

@contextmanager
def setup_ctx(params):
    with root_ctx(params) as params:
        yield global_setup_script(params)

def process(progress_info, params):
    params = params.copy()
    try:
        with setup_ctx(params) as params:
            result = test_execute(params)
            progress_info.incr()
            logger.info(progress_info)
    except (SkipError, StageError) as err:
        logger.debug('encountered non-fatal error: %s', err)
    except Exception as err:
        # unhandled Error
        logger.error('unhandled exception: %s(%s)', type(err), err)
        params['stage_exception'] = traceback.format_exc()
        params['stage_result'] = RESULT_ERROR

    return params

def main(conf, istream, ostream, test_whitelist, test_blacklist, stage_whitelist, stage_blacklist,
            tags_whitelist, tags_blacklist, no_action, parallel_instances=1):
    '''
    main worker function
    performs particular stages handling
    generates particular stage/test result list
    '''
    params = dict(test_whitelist=test_whitelist, test_blacklist=test_blacklist,
                    stage_whitelist=stage_whitelist, stage_blacklist=stage_blacklist,
                    tags_whitelist=tags_whitelist, tags_blacklist=tags_blacklist,
                   enabled=not no_action)
    params = load(istream, config_file=conf, augment=params)
    progress_info = ProgressInfo(params)

    tests = []
    for item in params:
        for test_stage in item['test_stages']:
            for test in item['test_stages'][test_stage]:
                tests.append(dict(test=dict(name=test, stage=test_stage), **item))

    from gevent.pool import Pool
    pool = Pool(size=parallel_instances)
    for result in pool.imap_unordered(lambda test: process(progress_info, test), tests):
        save_result(ostream, strip_ephemeral(result))

