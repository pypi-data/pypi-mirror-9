'''
the main report function module
'''
import logging
from ..work.data import load_yaml
from ..work.common import RESULT_PASSED
from result import get_overall_result

logger = logging.getLogger(__name__)

def main(config, istream, ostream, whitelist, verbose):
    result, ami_results = get_overall_result(load_yaml(istream), whitelist, verbose)
    print >>ostream, '# overal result: %s' % result
    for ami_result, ami_log in ami_results:
        for log_line in ami_log:
            print >>ostream, log_line
    # result passed -> 0 otherwise 1;
    # please note: result == passed and 0 or 1 -> 1 always
    return result != RESULT_PASSED and 1 or 0

