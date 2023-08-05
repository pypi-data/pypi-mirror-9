# This is the message object defined by the BigObjectService protocol
from bosrv.ttypes import *

from contextlib import contextmanager

# These are (de)serialization protocol + transport layer protocol supplied by
# 'thrift' framework
from thrift import Thrift
from thrift.protocol.TJSONProtocol import TJSONProtocolFactory
from thrift.transport.THttpClient import THttpClient

from urlparse import urlsplit

import sys

@contextmanager
def connect(url, secure=False, timeout=30):

    schema = secure and 'https' or 'http'
    o = urlsplit(url)
    addr_info = '{}://{}:{}'.format(schema, o.hostname, o.port)
    token = o.password

    class _connect():
        def __init__(self, addr_info):
            self.transport = THttpClient(uri_or_host=addr_info, path='/')
            # Assign default timeout on the connection client
            if timeout is None:
                self.transport.setTimeout(None)
            else:
                self.transport.setTimeout(timeout * 1000)
            # This is the API protocol for interacting with BigObjectService
            # on remote target
            import bosrv.BigObjectService as _BigObjectService
            BigObjectService = _BigObjectService.Client
            # Wrap in a (de)serialization protocol
            self.srv = BigObjectService(
                TJSONProtocolFactory().getProtocol(self.transport)
            )
            # insert a helper method
            setattr(self.srv, 'register_cleanup', self.register_cleanup)
            setattr(self.srv, 'settimeout', self.settimeout)

        def register_cleanup(self, clean_handle):
            self.clean_handle = clean_handle

        def settimeout(self, timeout):
            if timeout is None:
                self.transport.setTimeout(None)
            else:
                self.transport.setTimeout(timeout * 1000)

    conn = _connect(addr_info)
    try:
        conn.transport.open()
        yield (token, conn.srv)
    finally:
        try:
            conn.clean_handle()
        except AttributeError:
            pass # perhaps you did not register...
        finally:
            conn.transport.close()
