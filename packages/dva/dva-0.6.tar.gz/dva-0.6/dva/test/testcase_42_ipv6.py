""" This module contains testcase_42_ipv6 test """
from testcase import Testcase


class testcase_42_ipv6(Testcase):
    """
    Check that ipv6 networking is disabled
    """
    stages = ['stage1']
    tags = ['default']
    applicable = {'platform': '(?i)RHEL|BETA', 'version': 'OS (< 7.0)'}

    def test(self, connection, params):
        """ Perform test """

        prod = params['platform'].upper()
        if prod in ['RHEL', 'RHEL6', 'BETA']:
            self.get_return_value(connection, 'grep NETWORKING_IPV6=no /etc/sysconfig/network')
        else:
            self.get_return_value(connection, 'grep NETWORKING_IPV6=yes /etc/sysconfig/network')

        return self.log
