#
# bigobjsrv.py
# Python client wrapper with context management + unit test code
#
# Maintainer : Jeffrey Jen <yihungjen@macrodatalab.com>
#

import sys

# This is the message object defined by the BigObjectService protocol
from bosrv.ttypes import *

# These are (de)serialization protocol + transport layer protocol supplied by
# 'thrift' framework
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

def connect(addr_info, timeout=30):
    '''Helper method for establishing connection to the BigObject Service

    connect(addr_info [, timeout])

    Where addr_info is the standard hostname port tuple, and timtout is
    provided in milliseconds.  A default of 30s is used if unspecified

    When timout is None, the connection is never break off voluntarily only if
    remote hangup or that the underlying network failed.
    '''

    class _connect():
        def __init__(self, addr_info):
            # Make Buffered socket (Raw sockets are very slow)
            self.sock = TSocket.TSocket(*addr_info)
            # Assign default timeout on the connection client
            if timeout is None:
                self.sock.setTimeout(None)
            else:
                self.sock.setTimeout(timeout * 1000)
            self.transport = TTransport.TBufferedTransport(self.sock)
            # This is the API protocol for interacting with BigObjectService
            # on remote target
            import bosrv.BigObjectService as _BigObjectService
            BigObjectService = _BigObjectService.Client
            # Wrap in a (de)serialization protocol
            self.srv = BigObjectService(
                TBinaryProtocol.TBinaryProtocol(self.transport)
            )
            # insert a helper method
            setattr(self.srv, 'register_cleanup', self.register_cleanup)
            setattr(self.srv, 'settimeout', self.settimeout)

        def register_cleanup(self, clean_handle):
            self.clean_handle = clean_handle

        def settimeout(self, timeout):
            if timeout is None:
                self.sock.setTimeout(None)
            else:
                self.sock.setTimeout(timeout * 1000)

        def __enter__(self):
            self.transport.open()
            return self.srv

        def __exit__(self, type, value, traceback):
            try:
                self.clean_handle()
            except AttributeError:
                pass # perhaps you did not register...
            finally:
                self.transport.close()

    return _connect(addr_info)
