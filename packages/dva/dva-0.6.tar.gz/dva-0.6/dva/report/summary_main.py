'''
validation summary report function module
'''
import sys
import time
import logging
import bugzilla
import tempfile
import aggregate
from html import HTML
from ..tools.retrying import retrying, EAgain
from ..work.data import load_yaml, save_result
from ..work.common import RESULT_PASSED
from result import get_hwp_result
from gevent.pool import Pool
from gevent.coros import RLock
import yaml
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

logger = logging.getLogger(__name__)

def print_failed(data, aname, area, whitelist,area2='cloudhwname'):
    if not data:
        return
    agg_data = aggregate.flat(data, area)
    for name,data in agg_data.items():
        print('%s %s' % (aname, name[0]))
        for test in data:
            if test.has_key('test'):
                if test['test']['result'] != 'passed':
                    if test['test']['name'] not in whitelist:
                        print('   Failed test %s (%s)' % (test['test']['name'],test[area2]))
            else:
                if test['stage_result'] == 'skip':
                    print('!! Skipped - most likely unsupported instance type in region. (%s)' % test[area2])
                elif test['stage_result'] != 'passed':
                    print('!! Failed stage %s (%s)' % (test['stage_name'],test[area2]))

def print_xunit(data, aname, area):
    print('<?xml version="1.0" encoding="UTF-8"?><testsuites>')
    if not data:
        print('</testsuites>')
        return
    agg_data = aggregate.flat(data, area)
    error = {}
    fail = {}
    skip = {}
    total = {}
    testcase = {}
    testsuite = {}
    for name,data in agg_data.items():
        for test in data:
            classname = '%s-%s.%s' % (test['platform'],test['arch'],name[0])
            ami = name[0]
            if not (ami in error): error[ami] = 0
            if not (ami in fail): fail[ami] = 0
            if not (ami in total): total[ami] = 0
            if not (ami in skip): skip[ami] = 0
            total[ami] = total[ami]+1
            if test.has_key('test'):
                runtime = round(test['test']['end_time'] - test['test']['start_time'])
                try:
                    testcase[ami] = testcase[ami]+'<testcase classname="%s" name="%s.%s.%s" time="%d">' % (classname,test['cloudhwname'],test['test']['stage'],test['test']['name'],runtime)
                except KeyError:
                    testcase[ami] = '<testcase classname="%s" name="%s.%s.%s" time="%d">' % (classname,test['cloudhwname'],test['test']['stage'],test['test']['name'],runtime)
                if test['test']['result'] != 'passed':
                    fail[ami] = fail[ami]+1
                    testcase[ami] = testcase[ami]+'<error type="%s"><![CDATA[%s]]></error>' % (test['test']['result'],test['test']['log'])
            else:
                try:
                    testcase[ami] = testcase[ami]+'<testcase classname="%s" name="%s.%s">' % (classname,test['cloudhwname'],test['stage_name'])
                except KeyError:
                    testcase[ami] = '<testcase classname="%s" name="%s.%s">' % (classname,test['cloudhwname'],test['stage_name'])
                if test['stage_result'] != 'passed':
                    if test['stage_result'] == 'skip':
                        skip[ami] = skip[ami]+1
                    else:
                        error[ami] = error[ami]+1
                    testcase[ami] = testcase[ami]+'<error type="%s"><![CDATA[%s]]></error>' % (test['stage_result'],test['stage_exception'])
            testcase[ami] = testcase[ami]+'</testcase>\n'
        try:
            testsuite[ami] = testsuite[ami]+'<testsuite name="%s" tests="%d" errors="%d" failures="%d" skip="%d">\n' % (classname,total[ami],error[ami],fail[ami],skip[ami])
        except KeyError:
            testsuite[ami] = '<testsuite name="%s" tests="%d" errors="%d" failures="%d" skip="%d">\n' % (classname,total[ami],error[ami],fail[ami],skip[ami])
        testcase[ami] = testcase[ami]+'</testsuite>'

    for key in testsuite:
        print testsuite[key]
        print testcase[key]
    print('</testsuites>')

def main(config, istream,test_whitelist,compare,xunit):
    logger.debug('starting generation from file %s',istream)
    data = load_yaml(istream)
    comparelist = [str(item) for item in compare[0].split(',')]
    whitelist = [str(item) for item in test_whitelist[0].split(',')]
    for area in comparelist:
        area2 = 'cloudhwname'
        if area == 'cloudhwname':
            aname = 'HWNAME:'
            area2 = 'ami'
        elif area == 'region':
            aname = 'REGION:'
        else:
            area = 'ami'
            aname = 'AMI:'
        if xunit:
            print_xunit(data,aname,area)
        else:
            print_failed(data,aname,area,whitelist,area2)
