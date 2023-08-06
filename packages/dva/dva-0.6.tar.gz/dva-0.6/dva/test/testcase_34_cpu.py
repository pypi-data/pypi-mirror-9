""" This module contains testcase_34_cpu test """
from testcase import Testcase


class testcase_34_cpu(Testcase):
    """
    Check the number of cpu cores available
    """
    stages = ['stage1']
    tags = ['default', 'kernel']

    def test(self, connection, params):
        """ Perform test """

        if 'cpu' in params.keys():
            self.ping_pong(connection, 'cat /proc/cpuinfo | grep \'^processor\' | wc -l', params['cpu'])
        else:
            self.log.append({'result': 'skip',
                             'comment': 'cpu in hwp is not set'
                             })
        return self.log
