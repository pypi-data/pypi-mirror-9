""" This module contains testcase_24_yum_plugin test """
from testcase import Testcase


class testcase_24_yum_plugin(Testcase):
    """
    RHN plugin should be disabled
    """
    stages = ['stage1']
    applicable = {'platform': '(?i)RHEL|BETA', 'version': 'OS (>=5.5, <7.0)'}
    after = ['testcase_11_package_set']
    tags = ['default']

    # pylint: disable=W0613
    def test(self, connection, params):
        """ Perform test """

        self.get_return_value(connection, 'grep \'^enabled[[:space:]]*=[[:space:]]*[^0 ]\' /etc/yum/pluginconf.d/rhnplugin.conf', expected_status=1)
        return self.log
