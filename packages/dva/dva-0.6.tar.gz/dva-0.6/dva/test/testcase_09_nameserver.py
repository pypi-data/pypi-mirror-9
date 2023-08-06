""" This module contains testcase_09_nameserver test """
from testcase import Testcase


class testcase_09_nameserver(Testcase):
    """
    Check if DNS resolving works
    """
    stages = ['stage1']
    tags = ['default']

    def test(self, connection, params):
        """ Perform test """

        prod = params['platform'].upper()
        ver = params['version']
        if prod in ['RHEL', 'BETA'] and (ver.startswith('5.') or ver.startswith('6.')):
            self.get_return_value(connection, 'dig clock.redhat.com | grep 66.187.233.4', 30)
        else:
            self.get_return_value(connection, 'ping -c 5 clock.redhat.com', 30)
        return self.log
