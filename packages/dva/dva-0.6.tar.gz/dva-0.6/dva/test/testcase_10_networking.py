""" This module contains testcase_10_networking test """
from testcase import Testcase


class testcase_10_networking(Testcase):
    """
    Check for networking setup
    """

    stages = ['stage1']
    tags = ['default']

    # pylint: disable=W0613
    def test(self, connection, params):
        """ Perform test """

        self.get_return_value(connection, 'grep "^NETWORKING=yes" /etc/sysconfig/network')
        self.get_return_value(connection, 'egrep "^DEVICE=(|\\\")eth0(|\\\")" /etc/sysconfig/network-scripts/ifcfg-eth0')
        return self.log
