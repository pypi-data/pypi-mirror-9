'''yum version locks per product'''
from testcase import Testcase, SkipException
from distutils.version import LooseVersion

class testcase_43_yum_versionlock(Testcase):
    '''per product yum versionlocks'''
    stages = ['stage1']
    tags = ['default']

    # atm. relevant for sap only
    applicable = {'platform': '(?i)RHEL', 'product': '(?i)SAP'}

    def test(self, connection, params):
        '''perform test'''
        platform = params['platform'].upper()
        product = params['product'].upper()
        version = LooseVersion(params['version'])

        patterns = []
        if version == '6.5':
            patterns = [
                'kernel-2.6.32-431.29.2.el6.*',
                'kernel-firmware-2.6.32-431.29.2.el6.*',
                'kernel-headers-2.6.32-431.29.2.el6.*',
                'nss-softokn-freebl-3.14.3-12.el6_5.*',
                'nss-softokn-3.14.3-12.el6_5.*',
            ]

        assert patterns, 'no patterns specified for: %s/%s/%s' % \
            (platform, product, version)

        lines = self.get_result(connection, 'yum versionlock', 90).split('\r\n')
        assert all([pattern in lines for pattern in patterns]), \
            'not all versionlock patterns detected: %s; %s' % (patterns, lines)


