""" This module contains testcase_14_host_details test """
from testcase import Testcase
from dva.work.common import RESULT_FAILED
import json
import re


class testcase_14_host_details(Testcase):
    """
    Try to fetch host details from EC2 and compare with expectation
    """
    stages = ['stage1']
    tags = ['default']
    applicable = {'cloud': 'ec2'}

    def test(self, connection, params):
        """ Perform test """

        prod = params['platform'].upper()
        self.get_return_value(connection, '[ ! -z \'`curl http://169.254.169.254/latest/dynamic/instance-identity/signature`\' ]')
        json_str = self.match(connection, 'curl http://169.254.169.254/latest/dynamic/instance-identity/document', re.compile('.*({.*}).*', re.DOTALL))
        if json_str:
            try:
                jstruct = json.loads(json_str[0])
                if 'billingProducts' in jstruct.keys() and not jstruct['billingProducts'] is None:
                    billing_platform = jstruct['billingProducts'][0]
                else:
                    billing_platform = ''
                self.get_return_value(connection, '[ \'%s\' = \'%s\' ]' % (jstruct['imageId'], params['ami']))
                self.get_return_value(connection, '[ \'%s\' = \'%s\' ]' % (jstruct['architecture'], params['arch']))
                self.get_return_value(connection, '[ \'%s\' = \'%s\' ]' % (jstruct['region'], params['region']))
                if prod in ['RHEL', 'BETA']:
                    if params['itype'] == 'hourly':
                        self.get_return_value(connection, '[ \'%s\' = \'%s\' ]' % (billing_platform, 'bp-6fa54006'))
                    elif params['itype'] == 'access':
                        self.get_return_value(connection, '[ \'%s\' = \'%s\' ]' % (billing_platform, 'bp-63a5400a'))
            except KeyError as exc:
                self.log.append({'result': RESULT_FAILED, 'comment': 'failed to check instance details, ' + exc.message})
        else:
            self.log.append({'result': RESULT_FAILED, 'comment': 'failed to get instance details'})
        return self.log
