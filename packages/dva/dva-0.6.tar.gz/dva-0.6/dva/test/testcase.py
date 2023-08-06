""" Base test class """
import re
import logging
from stitches import Expect, ExpectFailed
from ..tools.logged import logged

logger = logging.getLogger(__name__)

class SkipException(RuntimeError):
    '''this test case should be skipped'''

class Testcase(object):
    """ Base test class """
    from ..tools.registry import TestRegistry
    __metaclass__ = TestRegistry

    datadir = '/usr/share/dva/data'
    stages = ['stage1']
    tags = ['default']

    def __init__(self):
        self.log = []
        self.logger = logger

    @logged(logger)
    def ping_pong(self, connection, command, expectation, timeout=10):
        """ Expect.ping_pong wrapper """
        result = {"command": command, "expectation": expectation}
        try:
            Expect.ping_pong(connection, command, expectation, timeout)
            result["result"] = "passed"
        except ExpectFailed, err:
            result["result"] = "failed"
            result["actual"] = err.message
        self.log.append(result)
        return result["result"]

    # pylint: disable=W0102
    @logged(logger)
    def match(self, connection, command, regexp, grouplist=[1], timeout=10):
        """ Expect.match wrapper """
        try:
            Expect.enter(connection, command)
            result = Expect.match(connection, regexp, grouplist, timeout)
            self.log.append({"result": "passed", "match": regexp.pattern, "command": command, "value": str(result)})
            return result
        except ExpectFailed, err:
            self.log.append({"result": "failed", "match": regexp.pattern, "command": command, "actual": err.message})
            return None

    @logged(logger)
    def get_result(self, connection, command, timeout=10):
        """ Expect.match wrapper """
        try:
            Expect.enter(connection, "echo '###START###'; " + command + "; echo '###END###'")
            regexp = re.compile(".*\r\n###START###\r\n(.*)\r\n###END###\r\n.*", re.DOTALL)
            result = Expect.match(connection, regexp, [1], timeout)
            self.log.append({"result": "passed", "command": command, "value": result[0]})
            return result[0]
        except ExpectFailed, err:
            self.log.append({"result": "failed", "command": command, "actual": err.message})
            return None

    @logged(logger)
    def get_return_value(self, connection, command, timeout=15, expected_status=0, nolog=False):
        """ Connection.recv_exit_status wrapper """
        status = connection.recv_exit_status(command + " >/dev/null 2>&1", timeout)
        if not nolog:
            if status == expected_status:
                self.log.append({"result": "passed", "command": command})
            else:
                self.log.append({"result": "failed", "command": command, "actual": str(status)})
        return status
