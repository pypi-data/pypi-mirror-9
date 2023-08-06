""" This module contains testcase_51_yum_package_install_sap test """
from testcase import Testcase


class testcase_51_yum_package_install_sap(Testcase):
    """
    Try to install package with yum
    """
    stages = ['stage1']
    tags = ['default', 'content']
    after = ['testcase_50_yum_package_install']
    applicable = {"platform": "(?i)rhel|beta", 'product': '(?i)SAP'}

    # pylint: disable=W0613
    def test(self, connection, params):
        """ Perform test """

        self.get_return_value(connection, 'yum clean all', 30)
        self.get_return_value(connection, 'yum repolist', 120)
        checkupdate = self.get_return_value(connection, 'yum check-update', 120, nolog=True)
        if not checkupdate in [0, 100]:
            # 100 means 'we have an update'
            self.log.append({"result": "failed", "command": "yum check-update", "actual": str(checkupdate)})
        self.get_return_value(connection, 'yum search zsh', 120)
        self.get_return_value(connection, 'yum -y install zsh', 180)
        self.get_return_value(connection, 'rpm -q --queryformat \'%{NAME}\' zsh', 30)
        self.get_return_value(connection, 'rpm -e zsh', 60)
        return self.log
