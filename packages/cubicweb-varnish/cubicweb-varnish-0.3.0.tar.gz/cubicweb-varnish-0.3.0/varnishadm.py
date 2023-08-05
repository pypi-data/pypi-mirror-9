"""simple varnish manager module.

The VarnishCLI opens a TCP socket to communicate with varnish CLI.

sources of inspiration include:

- http://pypi.python.org/pypi/varnish-admin-socket
- http://blog.hio.fr/2011/02/24/varnishpurge-sh.html
"""

import socket
import hashlib
import logging


class VarnishException(Exception):
    """varnish specific exceptions"""

class VarnishCLIError(VarnishException):
    """raised when CLI returned an error code (i.e. != 200)"""
    def __init__(self, code, msg):
        super(VarnishCLIError, self).__init__(msg)
        self.code = code
        self.errmsg = msg


class VarnishCLI(object):
    """
    typical usage:

    >>> varnish = VarnishCLI()
    >>> varnish.connect()
    >>> varnish.execute('status')
    >>> varnish.execute('purge /some/url')
    >>> varnish.close()
    """
    def __init__(self, host='127.0.0.1', port=6082, secret_file=None):
        self._host = host
        self._port = port
        self.secret = None if secret_file is None else file(secret_file).read()
        self._rfile = None
        self._wfile = None

    def connect(self, timeout=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(1)
        if timeout is not None:
            sock.settimeout(timeout)
        sock.connect( (self._host, self._port) )
        self._rfile = sock.makefile('r')
        self._wfile = sock.makefile('w')
        # now that we have read / write pipes, socket itself can be closed
        sock.close()
        code, response = self._receive()
        # status 107 indicates that authentication is necessary
        if code == 107:
            if self.secret is None:
                raise VarnishException('authentication required but no secret file specified')
            challenge = response.split('\n', 1)[0]

            auth_response = hashlib.sha256("%s\n%s%s\n" % (challenge, self.secret, challenge)).hexdigest()
            check_code, check_response = self._send("auth " + auth_response)
            if check_code != 200:
                raise VarnishException('authentication failed')

    def close(self):
        """closes socket"""
        if self._rfile is not None:
            self._rfile.close()
            self._rfile = None
        if self._wfile is not None:
            self._wfile.close()
            self._wfile = None

    def execute(self, cmd, value=''):
        """sends <cmd> <value> to varnish CLI

        If CLI returns an error status code (i.e. != 200), a `VarnishCLIError`
        exception is raised.

        :param cmd: the varnish CLI command (e.g. *status*, *purge.url*, ...)
        :return: the message sent back by CLI
        """
        code, response = self._send('%s %s' % (cmd, value))
        if code != 200:
            raise VarnishCLIError(code, response)
        return response

    def _receive(self):
        code, length = self._rfile.readline().split()
        msg = self._rfile.read(int(length)+1).strip()
        return int(code), msg

    def _send(self, instruction):
        self._wfile.write('%s\n' % instruction)
        self._wfile.flush()
        return self._receive()

    ## contextmanager interface ###############################################
    def __enter__(self):
        return self

    def __exit__(self, exc, exctype, traceback):
        self.close()


def varnish_cli_connect(host='127.0.0.1', port=6082, secret_file=None):
    varnish_cli = VarnishCLI(host, port, secret_file)
    varnish_cli.connect()
    return varnish_cli


def varnish_cli_connect_from_config(config):
    cnx = []
    varnishcli_hosts = config.get('varnishcli-hosts', ())
    for index, hostport in enumerate(varnishcli_hosts):
        host, port = hostport.split(':')
        secret = config['varnish-secrets'] and config['varnish-secrets'][index] or None
        try:
            cnx.append(varnish_cli_connect(host=host, port=int(port),
                                           secret_file=secret))
        except (VarnishException, socket.error), exc:
            logging.error('cube-varnish failed on %s:%s with %s' % (host, port, exc))
    return cnx

if __name__ == '__main__':
    #varnish_cli = varnish_cli_connect(secret_file='/etc/varnish/secret')
    varnish_cli = varnish_cli_connect()
    print varnish_cli.execute('status')
    varnish_cli.execute('purge.url', '^/$')
    varnish_cli.close()
