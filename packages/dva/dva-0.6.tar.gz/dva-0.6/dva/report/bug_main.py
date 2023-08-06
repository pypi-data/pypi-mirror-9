'''
the bugzilla report function module
'''
import sys
import time
import logging
import bugzilla
import tempfile
import aggregate
from ..tools.retrying import retrying, EAgain
from ..work.data import load_yaml, save_result, set_config_filename
from ..work.common import RESULT_PASSED, RESULT_SKIP, RESULT_WAIVED
from result import get_hwp_result
from gevent.pool import Pool
from gevent.coros import RLock
import yaml
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

logger = logging.getLogger(__name__)
DEFAULT_URL='https://bugzilla.redhat.com/xmlrpc.cgi'
DEFAULT_COMPONENT='images'
DEFAULT_PRODUCT='Cloud Image Validation'
MAXTRIES=40
SLEEP=3


def bugzilla_credentials(configfile):
    '''get bugzilla credentials from a config file'''
    configfile = set_config_filename(configfile)
    config = load_yaml(configfile)
    return config['bugzilla']['user'], config['bugzilla']['password']


@retrying(maxtries=MAXTRIES, sleep=SLEEP)
def connect(url, user, password):
    '''connect to bugzilla, return the bugzilla connection'''
    ret = bugzilla.RHBugzilla(url=url, user=user, password=password)
    if not ret:
        raise RuntimeError("Couldn't connect to bugzilla: %s %s %s" % (url, username, password))
    logger.debug('connected to bugzilla: %s %s %s %s', url, user, password, ret)
    return ret

@retrying(maxtries=MAXTRIES, sleep=SLEEP)
def create_bug(connection, summary, version, arch, component=DEFAULT_COMPONENT, bugzilla_product=DEFAULT_PRODUCT,
    op_sys='Linux', keywords=['TestOnly']):
    '''create particular bug'''
    return connection.createbug(product=bugzilla_product, component=component, version='RHEL' + str(version),
                rep_platform=arch, summary=summary, op_sys=op_sys, keywords=keywords)

@retrying(maxtries=MAXTRIES, sleep=SLEEP, final_exception=AssertionError)
def assert_bug(connection, bug):
    '''assert a bug exists'''
    try:
        return connection.getbug(bug.bug_id)
    except bugzilla.Fault as err:
        raise EAgain(err)

@retrying(maxtries=MAXTRIES, sleep=SLEEP)
def create_bug_log_attachment(connection, bug, ami, data):
    '''create bug attachment from data'''
    with tempfile.NamedTemporaryFile() as fd:
        logger.debug('%s got attachment tmpfile: %s', ami, fd.name)
        fd.write(yaml.dump(data, Dumper=Dumper))
        fd.seek(0)
        assert_bug(connection, bug)
        logger.debug('uploading %s log attachment', ami)
        attach_name = ami + '-log.yaml'
        res = connection.attachfile(bug.bug_id, fd, attach_name, filename=attach_name, contenttype='text/yaml', ispatch=False)
        logger.debug('uploading %s log attachmet done: %s', ami, res)

@retrying(maxtries=MAXTRIES, sleep=SLEEP)
def comment_bug(connection, bug, comment):
    res = assert_bug(connection, bug).addcomment(comment)
    logger.debug('bz %s added comment %s: %s', bug.bug_id, comment, res)


def process_ami_record(ami_key, ami_data, whitelist=[], user=None, password=None,
        url=DEFAULT_URL, component=DEFAULT_COMPONENT, bugzilla_product=DEFAULT_PRODUCT,
        verbose=False):
    '''process one ami record creating bug with comment per hwp'''
    connection = connect(url, user, password)
    summary = " ".join(ami_key)
    region, platform, product, version, arch, itype, ami = ami_key
    bug = create_bug(connection, summary, version, arch, component, bugzilla_product)
    create_bug_log_attachment(connection, bug, ami, ami_data)
    ami_result = RESULT_PASSED
    data = aggregate.nested(ami_data, 'cloudhwname')
    for hwp in data:
        sub_result, sub_log = get_hwp_result(data[hwp], whitelist, verbose)
        if sub_result not in [RESULT_PASSED, RESULT_SKIP] and ami_result == RESULT_PASSED:
            ami_result = sub_result
        bug.addcomment('# %s: %s\n%s' % (hwp, sub_result, '\n'.join(sub_log)))
    bug.setstatus(ami_result == RESULT_PASSED and 'VERIFIED' or 'ON_QA')
    return bug.bug_id, ami, ami_result

def process_ami_record_debug(ami_key, ami_data, whitelist=[], user=None, password=None,
        url=DEFAULT_URL, component=DEFAULT_COMPONENT, bugzilla_product=DEFAULT_PRODUCT,
        verbose=False):
    '''process one ami record creating bug with comment per hwp'''
    summary = " ".join(ami_key)
    ami = ami_key[-1]
    logger.debug('*** Summary for bug: %s', summary)
    logger.debug('*** Ami data: %s', ami_data)
    bug = 'not created'
    ami_result = RESULT_PASSED
    data = aggregate.nested(ami_data, 'cloudhwname')
    for hwp in data:
        sub_result, sub_log = get_hwp_result(data[hwp], whitelist, verbose)
        if sub_result not in [RESULT_PASSED, RESULT_SKIP] and ami_result == RESULT_PASSED:
            ami_result = sub_result
        logger.debug('.....adding comment: # %s: %s\n%s' % (hwp, sub_result, '\n'.join(sub_log)))
    logger.debug(".....setting status: %s", ami_result == RESULT_PASSED and 'VERIFIED' or 'ON_QA')
    return bug, ami, ami_result


def main(config, istream, ostream, test_whitelist, user=None, password=None, url=DEFAULT_URL, component=DEFAULT_COMPONENT,
         bugzilla_product=DEFAULT_PRODUCT, verbose=False, pool_size=128, debug_mode=False):
    user, password = bugzilla_credentials(config)
    logger.debug('got credentials: %s, %s', user, password)
    data = load_yaml(istream)
    whitelist = [str(item) for item in test_whitelist[0].split(',')]
    agg_data = aggregate.flat(data, 'region', 'platform', 'product', 'version', 'arch', 'itype',
                                'ami')
    pool = Pool(size=pool_size)
    if debug_mode:
        #There will be enhancement to have for each ami output in the file
        statuses = pool.map(lambda (key, data): process_ami_record_debug(key, data, whitelist, user=user,
            password=password, url=url, component=component, bugzilla_product=bugzilla_product),
            agg_data.items())
    else:
        statuses = pool.map(lambda (key, data): process_ami_record(key, data, whitelist, user=user,
            password=password, url=url, component=component, bugzilla_product=bugzilla_product),
            agg_data.items())
    for bug, ami, status in statuses:
        save_result(ostream, dict(bug=bug, id=ami, status=status))
    return all([status in (RESULT_PASSED,RESULT_WAIVED) for _, status, _ in statuses]) and 0 or 1

