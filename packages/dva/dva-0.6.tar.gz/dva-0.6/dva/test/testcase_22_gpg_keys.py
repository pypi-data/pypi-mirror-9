""" This module contains testcase_22_gpg_keys test """
from testcase import Testcase


class testcase_22_gpg_keys(Testcase):
    """
    Check that specified gpg keys are installed
    """

    stages = ['stage1']
    applicable = {'platform': '(?i)RHEL|BETA', 'version': 'OS (>=5.5, <7.0)'}
    tags = ['default']

    def test(self, connection, params):
        """ Perform test """

        self.ping_pong(connection, 'grep \'^gpgcheck=\' /etc/yum.repos.d/redhat-*.repo | cut -d\= -f2 | sort -uf | tr -d \' \'', '\r\n1\r\n')
        self.ping_pong(connection, 'rpm -qa gpg-pubkey* | wc -l', '\r\n2\r\n', 10)
        self.get_return_value(connection, 'rpm -q gpg-pubkey-2fa658e0-45700c69', 30)
        if params['version'].startswith('6.'):
            self.get_return_value(connection, 'rpm -q gpg-pubkey-fd431d51-4ae0493b', 30)
        elif params['version'].startswith('5.'):
            self.get_return_value(connection, 'rpm -q gpg-pubkey-37017186-45761324', 30)
        if params['platform'].upper() == 'BETA':
            self.get_return_value(connection, 'test -f /etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta')
        return self.log
