""" This module contains testcase_90_2_cgroups_kernel_bug914737 test """
import time
from testcase import Testcase


class testcase_90_2_cgroups_kernel_bug914737(Testcase):
    """
    Reproducer for kernel bug 914737
    """
    stages = ['stage1']
    tags = ['kernel']
    not_applicable = {'platform': '(?i)ATOMIC'}

    def test(self, connection, params):
        """ Perform test """

        prod = params['platform'].upper()
        ver = params['version'].upper()
        # pylint: disable=W0702
        try:
            memory = int(params['memory'])
        except:
            self.log.append({'result': 'skip', 'command': 'memory is not set in the profile'})
            return self.log
        self.get_return_value(connection, 'if [ ! -f /bin/cgset ]; then yum -y install libcgroup-tools ; fi', 240)
        self.get_return_value(connection, 'if ! mount | grep cgroup ; then service cgconfig start ; fi')
        connection.sftp.put('/usr/share/dva/data/memhog_with_forks.c', '/root/memhog_with_forks.c')
        if prod == 'FEDORA' and ver == '18':
            # ugly workaround - dependency problems :-(
            self.get_result(connection, 'if ! rpm -q gcc ; then yum -y install glibc audit gcc; fi', 300)
        else:
            self.get_result(connection, 'if ! rpm -q gcc ; then yum -y install gcc; fi', 300)
        self.get_return_value(connection, 'gcc /root/memhog_with_forks.c -o /root/memhog_with_forks')
        # Creating cpu and memory cgroups
        self.get_return_value(connection, 'for i in `seq 0 1000 `; do cgcreate -g cpu:/Group$i ; cgcreate -g memory:/Group$i ; done')
        # pylint: disable=C0301,W0702
        self.get_return_value(connection, 'for i in `seq 0 1000 `; do cgset -r memory.limit_in_bytes=' + str(memory) + ' /Group$i ; cgset -r cpu.shares=$i /Group$i ; done')
        try:
            # pylint: disable=C0301
            self.get_result(connection, 'for i in `seq 0 1000 `; do cgexec -g cpu:/Group$i -g memory:/Group$i /root/memhog_with_forks %i & echo $i ; done' % (memory // 1000000), 60)
            time.sleep(30)
            self.get_return_value(connection, 'id', 30)
            self.get_return_value(connection, 'killall memhog_with_forks ||:', 30)
        except:
            self.log.append({'result': 'failed', 'command': 'bug reproducer succeeded'})
        return self.log
