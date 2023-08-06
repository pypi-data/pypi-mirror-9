""" This module contains testcase_17_shells test """
from testcase import Testcase


class testcase_17_shells(Testcase):
    """
    Check for bash/nologin shells in /etc/shells
    """
    stages = ['stage1']
    tags = ['default']

    # pylint: disable=W0613
    def test(self, connection, params):
        """ Perform test """

        self.get_return_value(connection, 'grep \'bin/bash$\' /etc/shells')
        self.get_return_value(connection, 'grep \'bin/nologin$\' /etc/shells')
        return self.log
