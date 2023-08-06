""" This module contains testcase_97_collect_packagelist test """
from testcase import Testcase
import re


class testcase_97_collect_packagelist(Testcase):
    """
    Collect package list (debugging)
    """
    stages = ['stage0']
    tags = []

    # pylint: disable=W0613
    def test(self, connection, params):
        """ Perform test """

        packages = self.match(connection,
                              'rpm -qa --queryformat \'%{NAME},\' && echo',
                              re.compile('.*\r\n(.*),\r\n.*', re.DOTALL),
                              timeout=30)
        if packages is None:
            self.log.append({'result': 'failed', 'comment': 'Failed to get package set'})
        else:
            self.log.append({'result': 'passed', 'comment': packages[0]})
        return self.log
