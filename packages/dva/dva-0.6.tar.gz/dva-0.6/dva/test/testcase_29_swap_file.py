""" This module contains testcase_29_swap_file test """
from testcase import Testcase


class testcase_29_swap_file(Testcase):
    """
    Swap should be enabled and it should be possible to do swapoff/swapon
    (not applicable for t1.micro and hvm instances)
    """
    stages = ['stage1']
    applicable = {'cloudhwname': r'(?!t1\.micro)', 'virtualization': '(?!hvm)', 'arch': '(?!x86_64)'}
    tags = ['default']

    # pylint: disable=W0613
    def test(self, connection, params):
        """ Perform test """

        size = self.get_result(connection, 'parted -l | grep linux-swap | awk \'{print $4}\' | awk -F\'MB\' \'{print $1}\'', 15)
        partition = self.get_result(connection, 'parted -l | grep -B 6 swap | grep \'^Disk /\' | awk \'{print $2}\' | sed \'$s/.$//\' | head -1', 15)
        if size and partition:
            self.get_return_value(connection, '[ ' + size + ' -gt 0 ]')
            self.get_return_value(connection, 'swapoff ' + partition + ' ; echo')
            self.get_return_value(connection, 'swapon ' + partition, 30)
            self.get_return_value(connection, 'swapoff ' + partition + ' && swapon ' + partition, 30)
        return self.log
