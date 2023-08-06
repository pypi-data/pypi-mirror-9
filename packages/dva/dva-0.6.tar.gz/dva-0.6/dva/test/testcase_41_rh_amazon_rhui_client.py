""" This module contains testcase_41_rh_amazon_rhui_client test """
from testcase import Testcase
from distutils.version import LooseVersion
import re


class testcase_41_rh_amazon_rhui_client(Testcase):
    """
    Check for rh-amazon-rhui-client
    """
    tags = ['default']
    stages = ['stage1']
    applicable = {'cloud': '(?i)EC2', 'platform': '(?i)RHEL|BETA'}
    not_applicable = {'product': '(?i)ATOMIC'}

    def test(self, connection, params):
        """ Perform test """

        platform = params['platform'].upper()
        product = params['product'].upper()
        version = LooseVersion(params['version'])

        rpm_expr = None
        rpm_count = 1
        # what config rpm to assert
        # watch out for prefixes: rh-amazon-rhui-client.*
        # would match any client package name
        if platform == 'RHEL':
            if product == 'CLOUD':
                rpm_expr =  re.compile('rh-amazon-rhui-client-\d.*')
            elif product == "RHS":
                rpm_expr = re.compile('rh-amazon-rhui-client-jbeap5-\d.*')
            elif product == "JPEAP" and '6.0' <= version:
                rpm_expr = re.compile('rh-amazon-rhui-client-jbeap6-\d.*')
            elif product == "JBEWS" and '1.0' <= version < '2.0':
                rpm_expr = re.compile('rh-amazon-rhui-client-jbews1-\d.*')
            elif product == "JBEWS" and '2.0' <= version:
                rpm_expr = re.compile('rh-amazon-rhui-client-jbews2-\d.*')
            elif product == "GRID":
                rpm_expr = re.compile('rh-amazon-rhui-client-mrg-\d.*')
            elif product == 'SAP' and version == '6.5':
                rpm_expr = re.compile('rh-amazon-rhui-client-sap-hana-\d.*')
                rpm_count = 2 # exception
        elif platform == 'BETA':
            if product == 'CLOUD':
                rpm_expr = re.compile('rh-amazon-rhui-client-beta-\d.*')

        assert rpm_expr, 'spec for rhui config rpm missing: %s/%s/%s' % \
            (platform, product, version)

        # get all possible rhui config rpms installed
        rpm_log = self.get_result(connection, r'rpm -qa rh-amazon-rhui-client\*', 90)
        rpms = rpm_log.split()

        # check required rhui config rpm is installed
        assert rpms, 'no rhui config rpm installed'
        assert len(rpms) == rpm_count, 'expecting %s config rpm(s); got: %s instead' % \
            (rpm_count, rpms)
        # match expected pattern against detected rpms
        assert any([rpm_expr.match(rpm) for rpm in rpms]), \
            'wrong rhui config rpm instsalled: %s; expecting: %s' % (rpms, rpm_expr.pattern)


        return self.log
