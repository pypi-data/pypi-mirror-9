'''
params handling stuff
'''
import logging
from ..tools.retrying import retrying
from .. import cloud
from common import CLOUD_DRIVER_MAXWAIT
from functools import wraps
from data import DataError

logger = logging.getLogger
CLOUD_UPDATE_WAIT=3
UPDATE_ATTEMPTS=60

class UpdateError(RuntimeError):
    '''Update params failed'''


def when_enabled(fn):
    '''
    enabled-params check decorator; if not enabled; just return the params
    '''
    @wraps(fn)
    def wrapper(params):
        try:
            enabled = params['enabled']
        except KeyError as err:
            raise DataError('params misses %s' % err)
        if not enabled:
            return params
        return fn(params)
    return wrapper


@when_enabled
@retrying(maxtries=UPDATE_ATTEMPTS, sleep=CLOUD_UPDATE_WAIT, loglevel=logging.DEBUG, final_exception=UpdateError)
def reload(params):
    """
    update parameter fields fetching data from cloud
    """
    driver = cloud.get_driver(params['cloud'], logger, CLOUD_DRIVER_MAXWAIT)
    try:
        driver.update(params)
    except cloud.base.TemporaryCloudException as err:
        logger.debug('Temporary Cloud Exception: %s', err)
        raise EAgain(err)

