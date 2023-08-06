from plumbum import FG
from plumbum.cmd import dva
import requests

def process(pipeline):
    with open(conf_path) as conf_fd, open(input_path) as istream:
        dva 
