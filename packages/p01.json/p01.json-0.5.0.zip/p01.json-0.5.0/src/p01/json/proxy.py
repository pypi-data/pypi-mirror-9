##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import urllib
import copy
import logging
import socket

import zope.component
import z3c.json.proxy
from z3c.json import interfaces
from z3c.json.exceptions import ProtocolError
from z3c.json.exceptions import ResponseError

from p01.json.transport import Transport
from p01.json.transport import SafeTransport


class JSONRPCProxy(z3c.json.proxy.JSONRPCProxy):
    """JSON-RPC server proxy."""

    def __init__(self, uri, transport=None, encoding=None, verbose=None,
        jsonId=None, jsonVersion=z3c.json.proxy.JSON_RPC_VERSION,
        contentType='application/json-rpc'):
        self.contentType = contentType
        utype, uri = urllib.splittype(uri)
        if utype not in ("http", "https"):
            raise IOError, "Unsupported JSONRPC protocol"
        self.__host, self.__handler = urllib.splithost(uri)
        if not self.__handler:
            self.__handler = ""

        if transport is None:
            if utype == "https":
                transport = SafeTransport(contentType=self.contentType)
            else:
                transport = Transport(contentType=self.contentType)
        self.__transport = transport

        self.__encoding = encoding
        self.__verbose = verbose
        self.jsonId = jsonId or u'jsonrpc'
        self.jsonVersion = jsonVersion or JSON_RPC_VERSION
        self.error = None

    def __request(self, request):
        """call a method on the remote server.

        This will raise a ResponseError or return the JSON result dict
        """
        # apply encoding if any
        if self.__encoding:
            request = request.encode(self.__encoding)
        # start the call
        try:
            response = self.__transport.request(self.__host, self.__handler,
                request, verbose=self.__verbose)
            self.error = None
        except ResponseError, e:
            # catch error message
            self.error = unicode(str(e), 'utf-8')
            raise

        if isinstance(response, int):
            # that's just a status code response with no result
            logger.error('Received status code %s' % response)
        elif len(response) == 3:
            # that's a valid response format
            if (self.jsonId is not None and
                response.get('id') is not None and
                self.jsonId != response.get('id')):
                # different request id returned
                raise ResponseError("Invalid request id returned")
            if response.get('error'):
                # error mesage in response
                self.error = response['error']
                raise ResponseError("Received error from server: %s" %
                                    self.error)
            else:
                # only return the result if everything is fine
                return response['result']

        return response

    def __getattr__(self, name):
        """This let us call methods on remote server."""
        return z3c.json.proxy._Method(self.__request, name, self.jsonId,
            self.jsonVersion)

    def __repr__(self):
        return "<JSONProxy for %s%s>" % (self.__host, self.__handler)

    __str__ = __repr__
