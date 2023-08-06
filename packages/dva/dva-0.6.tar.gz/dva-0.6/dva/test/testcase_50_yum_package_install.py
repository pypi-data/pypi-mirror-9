""" This module contains testcase_50_yum_package_install test """
from testcase import Testcase
from distutils.version import LooseVersion


class testcase_50_yum_package_install(Testcase):
    """
    Try to install package with yum
    """
    stages = ['stage1']
    tags = ['default', 'content']
    after = ['testcase_31_subscription_management']
    applicable = {"platform": "(?i)rhel|beta", "version": "OS (>=5.5, !=6.0)"}

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

        # product-specific checks
        platform = params['platform'].upper()
        product = params['product'].upper()
        version = LooseVersion(params['version'])
        if product == 'SAP' and version == '6.5':
            self.get_return_value(connection, 'yum -y install tuned-profiles-sap-hana', 120)
            self.get_return_value(connection, 'rpm -q --queryformat \'%{NAME}\' tuned-profiles-sap-hana', 30)
        return self.log
