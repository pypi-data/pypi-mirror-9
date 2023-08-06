""" This module contains testcase_33_userdata test """
from testcase import Testcase


class testcase_33_userdata(Testcase):
    """
    Dumb test for userdata script execution
    """
    stages = ['stage1']
    tags = ['default']
    applicable = {"platform": "(?i)RHEL|BETA", "version": "OS ( > 6.3)"}

    def test(self, connection, params):
        """ Perform test """

        if params['userdata']:
            if self.get_result(connection, 'rpm -q --queryformat \'%{NAME}\n\' cloud-init', 5) == 'cloud-init':
                userdata_tested = False
                if params['userdata'].find('touch /userdata_test') != -1:
                    userdata_tested = True
                    self.get_return_value(connection, 'ls -l /userdata_test')
                if params['userdata'].find('yum -y install xdelta') != -1:
                    userdata_tested = True
                    self.get_return_value(connection, 'rpm -q xdelta')
                if not userdata_tested:
                    self.log.append({'result': 'skip',
                                     'comment': 'cannot test provided userdata'
                                     })
            else:
                self.log.append({'result': 'skip',
                                 'comment': 'no cloud-init package'
                                 })
        else:
            self.log.append({'result': 'skip',
                             'comment': 'no userdata'
                             })
        return self.log
