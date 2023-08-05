

import socket
import os
from six.moves import urllib


def guess_external_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 65056))
    return s.getsockname()[0]


def bind_zmq_socket(sock, address, port=None):
    endpoint = address if '://' in address else 'tcp://%s' % address
    p = urllib.parse.urlparse(endpoint)
    if port and p.port and p.port != port:
        raise ValueError('two port numbers given: %s and %s' % (p.port, port))

    if p.port:
        sock.bind(endpoint)
        port = p.port
    elif port:
        endpoint = '%s:%s' % (endpoint, port)
        sock.bind(endpoint)
    else:
        port = sock.bind_to_random_port(endpoint)
        endpoint = '%s:%s' % (endpoint, port)
    return endpoint, port


# adapted from https://github.com/mozilla-services/chaussette/
def create_socket(host, family=socket.AF_INET, type=socket.SOCK_STREAM,
                  backlog=2048, blocking=True, inheritable=False):
    if family == socket.AF_UNIX and not host.startswith('unix:'):
        raise ValueError('Your host needs to have the unix:/path form')
    if host.startswith('unix:'):
        family = socket.AF_UNIX

    if host.startswith('fd://'):
        fd = int(host[5:])
        sock = socket.fromfd(fd, family, type)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    else:
        sock = socket.socket(family, type)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if host.startswith('unix:'):
            filename = host[len('unix:'):]
            try:
                os.remove(filename)
            except OSError:
                pass
            sock.bind(filename)
        else:
            if ':' in host:
                host, port = host.rsplit(':', 1)
                port = int(port)
            else:
                host, port = '0.0.0.0', int(host)
            sock.bind((host, port))
        sock.listen(backlog)

    if blocking:
        sock.setblocking(1)
    else:
        sock.setblocking(0)

    # Required since Python 3.4 to be able to share a socket with a child
    # process.
    if inheritable and hasattr(os, 'set_inheritable'):
        os.set_inheritable(sock.fileno(), True)

    return sock
