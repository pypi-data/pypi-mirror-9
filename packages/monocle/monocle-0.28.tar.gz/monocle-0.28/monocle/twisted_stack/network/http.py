# -*- coding: utf-8 -*-
#
# by Steven Hazel

import urlparse
import logging

from monocle import _o, Return, VERSION, launch, log_exception
from monocle.callback import Callback
from monocle.stack.network.http import HttpHeaders, HttpRequest, HttpRouter, write_request, read_response, extract_response
from monocle.twisted_stack.eventloop import reactor
from monocle.twisted_stack.network import Service, SSLService, Client, SSLClient

from twisted.internet import ssl
from twisted.internet.protocol import ClientCreator
from twisted.web import server, resource

log = logging.getLogger("monocle.twisted_stack.network.http")

class HttpException(Exception): pass


class _HttpServerResource(resource.Resource):
    isLeaf = 1

    def __init__(self, handler):
        self.handler = handler

    def render(self, request):
        @_o
        def _handler(twisted_request):
            try:
                headers = HttpHeaders()
                for k, vs in twisted_request.requestHeaders.getAllRawHeaders():
                    for v in vs:
                        headers.add(k, v)

                # decode UTF-8 keys, matching tornado arg parsing behavior
                arguments = dict(
                    [(k.decode('utf-8'), v)
                     for k, v
                     in twisted_request.args.iteritems()])

                request = HttpRequest(
                    proto=twisted_request.clientproto,
                    host=twisted_request.getRequestHostname(),
                    method=twisted_request.method,
                    uri=twisted_request.uri,
                    arguments=arguments,
                    remote_ip=twisted_request.getClientIP(),
                    headers=headers,
                    body=twisted_request.content.getvalue())
                request._twisted_request = twisted_request

                value = yield self.handler(request)
                code, headers, content = extract_response(value)
            except Exception:
                log_exception()
                code, headers, content = 500, {}, "500 Internal Server Error"
            try:
                if twisted_request._disconnected:
                    return

                twisted_request.setResponseCode(code)
                headers.setdefault('Server', 'monocle/%s' % VERSION)
                grouped_headers = {}
                for name, value in headers.iteritems():
                    if name in grouped_headers:
                        grouped_headers[name].append(value)
                    else:
                        grouped_headers[name] = [value]
                for name, value in grouped_headers.iteritems():
                    twisted_request.responseHeaders.setRawHeaders(name, value)
                twisted_request.write(content)

                # close connections with a 'close' header
                if headers.get('Connection', '').lower() == 'close':
                    twisted_request.channel.persistent = False

                twisted_request.finish()
            except Exception:
                log_exception()
                raise
        _handler(request)
        return server.NOT_DONE_YET


class HttpServer(Service, HttpRouter):
    def __init__(self, port, handler=None, bindaddr="", backlog=128):
        HttpRouter.__init__(self)
        self.port = port
        self.handler = handler
        self.bindaddr = bindaddr
        self.backlog = backlog
        self._twisted_listening_port = None
        self.factory = server.Site(_HttpServerResource(self.handle_request))


class HttpsServer(SSLService, HttpRouter):
    def __init__(self, port, ssl_options, handler=None, bindaddr="", backlog=128):
        HttpRouter.__init__(self)
        self.port = port
        self.ssl_options = ssl_options
        self.handler = handler
        self.bindaddr = bindaddr
        self.backlog = backlog
        self._twisted_listening_port = None
        self.factory = server.Site(_HttpServerResource(self.handle_request))
