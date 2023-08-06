""" This module contains testcase_27_yum_repos test """
from testcase import Testcase
from dva.work.common import RESULT_FAILED, RESULT_SKIP
import yaml


class testcase_27_yum_repos(Testcase):
    """
    Check for enabled yum repos
    """
    stages = ['stage1']
    applicable = {'platform': '(?i)RHEL|BETA', 'version': 'OS (>=5.5, !=6.0)'}
    after = ['testcase_24_yum_plugin']
    tags = ['default', 'content']

    def test(self, connection, params):
        """ Perform test """

        plat = params['platform'].upper()
        prod = params['product'].upper()
        ver = params['version']
        if connection.rpyc is None:
            self.log.append({
                'result': RESULT_FAILED,
                'comment': 'test can\'t be performed without RPyC connection'})
            return self.log
        repos = {}
        rbase = connection.rpyc.modules.yum.YumBase()
        for repo in rbase.repos.repos:
            repos[repo] = rbase.repos.repos[repo].isEnabled()

        # figure out whether expected repos match repos
        with open(self.datadir + '/repos.yaml') as expected_repos_fd:
            all_repos = yaml.safe_load(expected_repos_fd)
        try:
            expected_repos_ = all_repos[params['region']]['%s_%s' % (prod, ver)]
        except KeyError:
            try:
                expected_repos_ = all_repos[params['region']]['%s_%s' % (plat, ver)]
            except KeyError:
                self.log.append({
                    'result': RESULT_FAILED,
                    'comment': 'unsupported region and/or platform-version combination'})
                return self.log
        # expand %region%
        expected_repos = {}
        for key, val in expected_repos_.items():
            expected_repos[key.replace('%region%', params['region'])] = val
        ret = {
            'expected repos': expected_repos,
            'actual repos': repos
        }
        ret['result'] = expected_repos == repos and 'passed' or 'failed'
        self.log.append(ret)
        return self.log
