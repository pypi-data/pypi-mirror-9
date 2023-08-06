#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import sys

from .genericweaver import BaseWeaver
from .helpers import Helpers
from .httpweaver import BaseHttpWeaver


class TornadoHttpWeaver(BaseHttpWeaver):
    @staticmethod
    def getMappedHeaderName(name):
        return name

    @staticmethod
    def getExtraHeadersMapping(prefix,headers,remap):
        mapping = {}
        if (prefix is None) or (headers is None) or (len(headers) <= 0):
            return mapping
        
        for name in headers:
            key = name
            if remap:
                key = TornadoHttpWeaver.getMappedHeaderName(name)
            if Helpers.isEmpty(key):
                continue
            mapping[key] = BaseHttpWeaver.getMappedHeaderName(prefix, name)

        return mapping

    @staticmethod
    def getRemoteAddress(request):
        """
        Returns the IP of the request, accounting for the possibility of being behind a proxy.
        See http://stackoverflow.com/questions/9420886/retrieve-browser-headers-in-python
        """
        ip = request.headers.get('X-Forwarded-For', None)
        if ip:
            # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
            proxies = ip.split(", ") 
            ip = proxies[0]
        else:
            ip = request.remote_ip
        return ip

    @staticmethod
    def getRequestHeadersMapping(args):
        return TornadoHttpWeaver.getExtraHeadersMapping(BaseHttpWeaver.REQUEST_HEADER_PREFIX, args.get(BaseHttpWeaver.REQ_HEADERS_CONFIG_PROP, None), False)

    def fillExtraRequestHeaders(self,hdrs,props):
        return BaseHttpWeaver.fillExtraMappedHeaders(hdrs, self.reqHeadersMappings, props)

    @staticmethod
    def getResponseHeadersMapping(args):
        return TornadoHttpWeaver.getExtraHeadersMapping(BaseHttpWeaver.RESPONSE_HEADER_PREFIX, args.get(BaseHttpWeaver.RSP_HEADERS_CONFIG_PROP, None), False)

    def fillExtraResponseHeaders(self,hdrs,props):
        return BaseHttpWeaver.fillExtraMappedHeaders(hdrs, self.rspHeadersMappings, props)
    
    def __init__(self, logFactory, args, dispatcher):
        super(TornadoHttpWeaver,self).__init__("tornado-http", logFactory, args, dispatcher)
        self.reqHeadersMappings = TornadoHttpWeaver.getRequestHeadersMapping(args)
        self.rspHeadersMappings = TornadoHttpWeaver.getResponseHeadersMapping(args)
        self.TORNADO_TRACEID_HEADER = TornadoHttpWeaver.getMappedHeaderName(BaseHttpWeaver.TRACEID_HEADER)

        from tornado.web import RequestHandler, HTTPError
        old_execute = RequestHandler._execute
        thisWeaver = self

        # @gen.coroutine
        def _execute(self, transforms, *args, **kwargs):
            error = None
            request = self.request
            startCorrelation = thisWeaver.startCorrelationContext('tornado', request.headers.get(thisWeaver.TORNADO_TRACEID_HEADER, None))
            startTime = BaseWeaver.timestampValue()
            try:
                response = old_execute(self, transforms, *args, **kwargs)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()
            endCorrelation = thisWeaver.endCorrelationContext(startCorrelation)

            props = { 
                'objecttype': 'tornado.web.RequestHandler',
                'function': '_execute',
                'signature': '(self, transforms, args, kwargs)'
            }

            BaseWeaver.setTraceEssenceCorrelation(props, startCorrelation, endCorrelation)

            headers = request.headers
            props = BaseHttpWeaver.parseProtocol(request.version, props)
            props = BaseHttpWeaver.fillRequestDetails(props=props,
                                              uri=request.uri,
                                              method=request.method,
                                              requestSize=headers.get('Content-Length', None),
                                              remoteAddress=TornadoHttpWeaver.getRemoteAddress(request),
                                              # remoteUser=request.META.get('REMOTE_USER', ""),
                                              userAgent=headers.get('User-Agent', ""))
            thisWeaver.fillExtraRequestHeaders(headers, props)

            if error is None:
                thisWeaver.fillExtraResponseHeaders(self._headers, props)
                BaseHttpWeaver.fillResponseDetails(props=props,
                                                   statusCode=self.get_status(),
                                                   responseSize=self._headers.get('Content-Length', None))
            elif isinstance(error, HTTPError):
                BaseHttpWeaver.fillResponseDetails(props=props, statusCode=error.status_code)
                
            thisWeaver.dispatch(startTime, endTime, props, error)

            if error is None:
                return response
            else:
                raise error

        RequestHandler._execute = _execute