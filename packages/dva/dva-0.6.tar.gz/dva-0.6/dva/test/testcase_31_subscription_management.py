""" This module contains testcase_31_subscription_management test """
from testcase import Testcase
from distutils.version import LooseVersion

class testcase_31_subscription_management(Testcase):
    """
    Subscription manager shoud be disabled
    """
    stages = ['stage1']
    applicable = {'platform': '(?i)RHEL|BETA', 'version': 'OS (> 5.5)'}
    after = ['testcase_27_yum_repos']
    tags = ['default', 'content']

    def test(self, connection, params):
        """ Perform test """
        version = LooseVersion(params['version'])
        # following versions shouldn't contain subscription-manager at all
        if version < '5.9' or '6.0' >= version < '6.3':
            self.ping_pong(
                connection,
                'rpm -q subscrioption-manager || echo SUCCESS',
                expectation='\r\nSUCCESS\r\n',
            )
            return self.log

        # check subscription-manager plugin is disabled
        self.ping_pong(
            connection,
            'yum --disablerepo=\'*\' -v repolist',
            expectation='Not loading "subscription-manager" plugin',
            timeout=30
        )
        # check subscription-manager plugin can be enabled
        self.ping_pong(
            connection,
            'yum --enableplugin=subscription-manager --disablerepo=\'*\' -v repolist',
            expectation='Loading "subscription-manager" plugin',
            timeout=30
        )
        if params['version'].startswith('5.'):
            # RHEL5.* is going to be updated to match newer major versions gradually
            result = self.ping_pong(
                connection,
                'subscription-manager list',
                expectation='Installed Product Status',
                timeout=90
            )
            if result == 'failed':
                # warn in case there's no subscription shown
                self.log[-1]['result'] = 'warning'
        else:
            self.ping_pong(
                connection,
                'subscription-manager list',
                expectation='Installed Product Status',
                timeout=90
            )
        return self.log
