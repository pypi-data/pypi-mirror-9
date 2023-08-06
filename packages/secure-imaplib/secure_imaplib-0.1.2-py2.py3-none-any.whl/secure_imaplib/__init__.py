# secure_smtplib - secure SMTP classes from mercurial
#
# Copyright 2006 Matt Mackall <mpm@selenic.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 3 or any later version.

import imaplib
import socket
import ssl


class IMAP4_SSL(imaplib.IMAP4_SSL):
    def __init__(self, sslkwargs, **kwargs):
        self._sslkwargs = sslkwargs
        imaplib.IMAP4_SSL.__init__(self, **kwargs)

    def open(self, host='', port=imaplib.IMAP4_SSL_PORT):
        """Setup connection to remote server on "host:port".
            (default: localhost:standard IMAP4 SSL port).
        This connection will be used by the routines:
            read, readline, send, shutdown.
        """
        self.host = host
        self.port = port
        self.sock = socket.create_connection((host, port))
        self.sslobj = ssl.wrap_socket(
            self.sock,
            self.keyfile,
            self.certfile,
            **self._sslkwargs
        )
        self.file = self.sslobj.makefile('rb')
