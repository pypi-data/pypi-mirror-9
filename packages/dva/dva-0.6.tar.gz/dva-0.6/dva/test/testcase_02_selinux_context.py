""" This module contains testcase_02_selinux_context test """
import re
import yaml
import os
import tempfile
from testcase import Testcase
from collections import defaultdict

EXCLUDED_PATHS = defaultdict(lambda: ['/mnt', '/proc', '/sys'], {
    'ATOMIC': [ '/var/mnt', '/proc', '/sys', '/sysroot/' ]
})

def restorecon_cmd(platform):
    '''return a restorecon cmd  to execute remotely to get list of changes'''
    return 'restorecon -R -v -n ' +  ' '.join(map(lambda path: '-e ' + path, EXCLUDED_PATHS[platform])) + \
        ''' | sed -e 's, context , ,' -e 's,^restorecon reset ,,' '''

class testcase_02_selinux_context(Testcase):
    """
    Check if the kickstart restores selinux appropriately
    """
    stages = ['stage1']
    tags = ['default']

    def test(self, connection, params):
        """ Perform test """

        prod = params['platform'].upper()
        ver = params['version']
        #get the restorecon output file
        self.ping_pong(connection, restorecon_cmd(prod) + " > /tmp/restorecon_output.txt && echo SUCCESS",
                       "\r\nSUCCESS\r\n", 260)
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.close()
        connection.sftp.get('/tmp/restorecon_output.txt', tfile.name)
        output = open(tfile.name, 'r')
        result = output.read()
        output.close()
        os.unlink(tfile.name)
        # convert output file into a dictionary to be able to compare with allowed selinux exclusions
        result = result.split("\n")
        result.pop()
        restorecon_dict = {}
        for line in result:
            filename = line.split(" ")[0]
            context = line.split(" ")[1]
            source_context = context.split(":")[2]
            destination_context = context.split(":")[5]
            restorecon_dict[filename] = [source_context, destination_context]
        #figure out if there are new/lost entries or the restorecon output matched the list of allowed exclusions
        with open(self.datadir + '/selinux_context.yaml') as selinux_context:
            # by default, no SELinux issues are expected for untracked platform/version combinations
            context_exclusions = defaultdict(lambda: {}, yaml.load(selinux_context))['%s_%s' % (prod, ver)]

        lost_entries = []
        for filename in context_exclusions:
            pattern = re.compile('%s' % filename)
            matched = False
            for filename_rest in restorecon_dict:
                match_result = pattern.match(filename_rest)
                if match_result and context_exclusions[filename] == restorecon_dict[filename_rest]:
                    matched = True
                    break
            if not matched:
                lost_entries.append([filename, context_exclusions[filename]])

        new_entries = []
        for filename_rest in restorecon_dict:
            matched = False
            for filename in context_exclusions:
                pattern = re.compile('%s' % filename)
                match_result = pattern.match(filename_rest)
                if match_result and context_exclusions[filename] == restorecon_dict[filename_rest]:
                    matched = True
                    break
            if not matched:
                new_entries.append([filename_rest, restorecon_dict[filename_rest]])

        if new_entries == [] and lost_entries != []:
            self.log.append({'result': 'warning', 'comment': '\nLost entries:' + str(lost_entries)})
        if new_entries == lost_entries == []:
            self.log.append({'result': 'passed', 'comment': 'No new or lost entries detected. Restorecon output file matches with the list of allowed SElinux context discrepancies.'})
        if new_entries != []:
            self.log.append({'result': 'failed', 'comment': '\nFail.New entries detected:' + str(new_entries) + '\nLost entries:' + str(lost_entries)})
        return self.log
