""" This module contains testcase_38_rclocal_checksum test """
from testcase import Testcase


class testcase_38_rclocal_checksum(Testcase):
    """
    Get checksum for /etc/rc.d/rc.local (debugging purposes)
    """
    tags = []
    stages = ['stage1']

    # pylint: disable=W0613
    def test(self, connection, params):
        """ Perform test """

        self.get_result(connection, '[ -f /etc/rc.d/rc.local ] && md5sum /etc/rc.d/rc.local || echo "no rc.local"')
        return self.log
