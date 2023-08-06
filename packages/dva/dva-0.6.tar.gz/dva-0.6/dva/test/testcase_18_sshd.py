""" This module contains testcase_17_sshd test """
from testcase import Testcase


class testcase_18_sshd(Testcase):
    """
    Sshd service shoud be on, password authentication shoud be disabled
    """
    stages = ['stage1']
    tags = ['default']

    def test(self, connection, params):
        """ Perform test """

        prod = params['platform'].upper()
        ver = params['version']
        is_systemd = self.get_result(connection, 'rpm -q systemd > /dev/null && echo True || echo False')
        if is_systemd == 'True':
            self.get_return_value(connection, 'systemctl is-active sshd.service')
        else:
            # pylint: disable=C0301
            self.get_return_value(connection, 'chkconfig --list sshd | grep \'0:off[[:space:]]*1:off[[:space:]]*2:on[[:space:]]*3:on[[:space:]]*4:on[[:space:]]*5:on[[:space:]]*6:off\'')
            self.get_return_value(connection, 'service sshd status | grep running')
        if not (prod in ['RHEL', 'BETA'] and (ver in ['5.5', '5.6'])):
            # Password authentication was allowed before 5.7
            self.get_return_value(connection, 'grep \'PasswordAuthentication no\' /etc/ssh/sshd_config')
        return self.log
