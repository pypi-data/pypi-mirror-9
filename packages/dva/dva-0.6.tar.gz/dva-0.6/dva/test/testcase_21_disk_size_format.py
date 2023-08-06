""" This module contains testcase_21_disk_size_format test """
import re
from testcase import Testcase
from distutils.version import LooseVersion


def mount2fsys(prod, vers, mpoint):
    '''return expected fsys for particular mountpoint/platform/version combination'''
    if vers < '6.0':
        # ext3 for RHEL5 any mpoint
        return 'ext3'
    elif vers < '7.0' and mpoint == '/':
        # ext4 for / in RHEL6
        return 'ext4'
    elif prod in ('RHEL', 'BETA') and vers >= '7.0' and mpoint == '/':
        # xfs for / in RHEL7 and newer
        return 'xfs'
    elif prod == 'ATOMIC':
        # xfs for atomic, save for /var/mnt
        if mpoint == '/var/mnt':
            return 'ext3'
        else:
            return 'xfs'
    # ext3 for all other FS in other OSes
    return 'ext3'


class testcase_21_disk_size_format(Testcase):
    """
    Check filesystems:
    - / shoud be ext3 on RHEL5, ext4 otherwise
    - other filesystems shoud be always be ext3
    - all filesystems show have at least 4gb of available space (weird)
    """
    stages = ['stage1']
    tags = ['default']
    applicable = {'platform': '(?i)RHEL|BETA|ATOMIC'}

    def test(self, connection, params):
        """ Perform test """

        prod = params['platform'].upper()
        vers = LooseVersion(params['version'])

        disks = self.get_result(connection, 'mount | grep \'^/dev\' | awk \'{print $1}\'')
        if disks:
            for disk in set(disks.split()):
                # check free space
                self.get_return_value(connection, '[ `df -k %s | awk \'{ print $2 }\' | tail -n 1` -gt 3937219 ]' % disk)
                # check mount point fstype
                mpoint = self.match(connection, 'echo \'###\' ;mount | grep \'^%s\' | awk \'{print $3}\'; echo \'###\'' % disk,
                                    re.compile('.*\r\n###\r\n(.*)\r\n###\r\n.*', re.DOTALL))
                fsys = self.match(connection, 'echo \'###\' ;mount | grep \'^%s\' | awk \'{print $5}\'; echo \'###\'' % disk,
                                  re.compile('.*\r\n###\r\n(.*)\r\n###\r\n.*', re.DOTALL))
                if not mpoint or not fsys:
                    continue
                # mpoint/fsys are a match-groups tuple
                # mpoint/fsys can be multiple values on e.g. ATOMIC
                for mpoint, fsys in zip(mpoint[0].split(), fsys[0].split()):
                    expected_fsys = mount2fsys(prod, vers, mpoint)
                    self.log.append({'expected': mpoint + ': ' + expected_fsys, 'actual': fsys})
                    assert fsys == expected_fsys
                    self.log[-1]['result'] = 'passed'
        return self.log
