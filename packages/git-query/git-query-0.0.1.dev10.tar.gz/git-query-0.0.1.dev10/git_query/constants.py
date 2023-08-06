import fcntl
import os
import struct
import termios

try:
    USERNAME = os.environ['GERRIT_USERNAME']
    TOKEN = os.environ['GERRIT_TOKEN']
    HOST = os.environ['GERRIT_HOST']
except KeyError as e:
    raise Exception('Could not find environment variable ' + str(e))

LOGIN_URL = '%s/login/q/status:open,n,z' % HOST
HTTP_PASSWORD_URL = '%s/accounts/self/password.http' % HOST
SSH_KEYS_URL = '%s/a/accounts/self/sshkeys' % HOST
CHANGES_URL = '%s/a/changes/' % HOST

# credits: http://stackoverflow.com/a/3010495
h, TERM_WIDTH, hp, wp = struct.unpack(
    'HHHH',
    fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0))
)

MIN_WIDTH = 60
