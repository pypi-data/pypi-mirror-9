""" This module contains testcase_190_cds_hostnames"""
from testcase import Testcase

class testcase_190_cds_hostnames(Testcase):
    """
    ensure cdses are resolved properly
    """
    stages = ['stage1']
    tags = ['default']

    def test(self, connection, params):
        """ Perform test """
        # contains items such as rhui2-cds02.eu-1-central.aws.ce.redhat.com
        cds_hostnames = [ "rhui2-cds0%s.%s.aws.ce.redhat.com" % (i, params['region']) \
            for i in range(1, 3)]
        # try resolving
        for hostname in cds_hostnames:
            self.get_result(connection, 'getent hosts %s' % hostname, timeout=2)
        return self.log
