import sys
from gevent import monkey; monkey.patch_all()
from gevent import socket
socket.setdefaulttimeout(3)
