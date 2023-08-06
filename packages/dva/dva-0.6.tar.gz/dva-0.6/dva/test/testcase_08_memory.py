""" This module contains testcase_08_memory test """
from testcase import Testcase
import re


class testcase_08_memory(Testcase):
    """
    Check for available amount of memory
    """
    stages = ['stage1', 'stage2']
    tags = ['default', 'kernel']

    def test(self, connection, params):
        """ Perform test """

        if not 'memory' in params.keys():
            self.log.append({'result': 'skip', 'comment': 'memory parameter is not set, nothing to check'})
        else:
            values = self.match(connection, 'grep --color=none \'MemTotal:\' /proc/meminfo', re.compile(r'.*\r\nMemTotal:\s*([0-9]+) ', re.DOTALL))
            if values:
                self.get_return_value(connection, '[ %s -gt %s ]' % (values[0], params['memory']))
        return self.log
