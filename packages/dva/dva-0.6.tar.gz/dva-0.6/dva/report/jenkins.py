'''
tool for uploading data to Jenkins
'''
import sys
import time
import logging
import tempfile
import json
import requests
import time
import urllib3
import StringIO
import xml.etree.ElementTree as ET
from ..tools.retrying import retrying, EAgain
from ..work.data import load_yaml, save_result
from ..work.common import RESULT_PASSED

logger = logging.getLogger(__name__)

def main(config, istream, job, hashtag, desc, login, passwd, report_empty=False):
    file_data = istream.read()
    # check the data
    report_tree = ET.parse(StringIO.StringIO(file_data))
    if not report_tree.getroot().getchildren() and not report_empty:
        # nothing to report and user not interested in reporting empty result
        print "nothing to report..."
        return
    params = {"parameter": [{'name':'report.xml', 'file': 'file0'},{"name": "desc", "value": hashtag}]}
    data, content_type = urllib3.encode_multipart_formdata([
        ("file0", (istream.name, file_data)),
        ("json", json.dumps(params)),
        ("Submit", "Build"),
        ])
    url = job + 'build'
    r = requests.post(url, auth=(login, passwd), data=data, headers={"content-type": content_type})
    if not r.ok:
        print "Authentification failure."
        exit(1)
    print "Waiting 10s for build to be finished."
    time.sleep(10)
    url = job + 'api/xml'
    xpath_str = "//build//*[contains(text(),'"+ hashtag +"')]/../../../url"
    params = {'depth': '1', 'xpath': xpath_str, 'wrapper': 'list'}
    r = requests.get(url, auth=(login, passwd), params=params)
    
    tree = ET.fromstring(r.text.replace('</url>','</url>\n'))
    notags = ET.tostring(tree, encoding='utf8', method='text')
    job_number = notags.splitlines()[0].rsplit('/',2)[1]

    url = job + 'default/' + job_number + '/testReport/submitDescription'
    params = {'description': desc}
    r = requests.get(url, auth=(login,passwd), params=params)

    print "Return code: " + str(r.status_code)
