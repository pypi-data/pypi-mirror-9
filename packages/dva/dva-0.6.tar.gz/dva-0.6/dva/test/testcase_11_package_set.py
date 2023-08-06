""" This module contains testcase_11_package_set test """
import os
import re
from testcase import Testcase, SkipException
from dva.work.data import load_yaml
FILENAME_FIELDS = ['platform', 'product', 'version']


class testcase_11_package_set(Testcase):
    """
    Check that all packages specified in list
    /usr/share/dva/data/packages_<name>  are present
    """
    stages = ['stage1']
    applicable = {'platform': '(?i)RHEL|BETA|FEDORA'}
    tags = ['default']

    def package_list_filename(self, params):
        '''construct package list filename based on the params provided'''
        filename = 'packages_' + '_'.join([params[field].lower() for field in FILENAME_FIELDS]) + '.yaml'
        # beta packages are the same as rhel
        filename = filename.replace('beta', 'rhel')
        path = os.path.sep.join([self.datadir, filename])
        if not os.path.exists(path):
            raise SkipException('packages list %s not found' % path)
        return path

    def required_packages(self, params):
        '''return set of required packages'''
        with open(self.package_list_filename(params)) as fd:
            ret = set(load_yaml(fd))
        return ret
        

    def test(self, connection, params):
        """ Perform test """
        # load expected package list
        package_set_required = self.required_packages(params)

        # fetch packages installed on the instance
        packages_log = self.match(connection,
                              'rpm -qa --queryformat \'%{NAME},\' && echo',
                              re.compile('.*\r\n(.*),\r\n.*', re.DOTALL),
                              timeout=30)[0]
        package_set_got = set(packages_log.split(','))

        # augment userdata-installed packages
        if params['userdata'].find('yum -y install xdelta') != -1:
            package_set_got.discard('xdelta')

        difference = package_set_required.difference(package_set_got)
        difference_new = package_set_got.difference(package_set_required)
        
        self.log.append({'result': 'passed', 'comment': 'Newly introduced packages: ' + str(sorted(list(difference_new)))})
        if params['platform'].upper() == 'BETA' and len(difference) > 1:
            self.log.append({'result': 'failed', 'comment': 'Beta may lack not more than 1 package: ' + str(sorted(list(difference)))})
        elif len(difference) > 1:
            self.log.append({'result': 'failed', 'comment': 'some packages are missing: ' + str(sorted(list(difference)))})
        else:
            self.log.append({'result': 'passed', 'comment': 'All required package are included'})
        return self.log
