#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import sys

from .helpers import Helpers
from .genericweaver import BaseWeaver
from .httpweaver import BaseHttpWeaver

class BottleHttpWeaver(BaseHttpWeaver):
    @staticmethod
    def getMappedHeaderName(name):
        if Helpers.isEmpty(name):
            return name
        
        name = name.upper()
        name = name.replace('-', '_')
        return "HTTP_%s" % name

    @staticmethod
    def getExtraHeadersMapping(prefix,headers,remap):
        mapping = {}
        if (prefix is None) or (headers is None) or (len(headers) <= 0):
            return mapping
        
        for name in headers:
            key = name
            if remap:
                key = BottleHttpWeaver.getMappedHeaderName(name)
            if Helpers.isEmpty(key):
                continue
            mapping[key] = BaseHttpWeaver.getMappedHeaderName(prefix, name)

        return mapping

    @staticmethod
    def getRemoteAddress(environ):
        """
        Returns the IP of the request, accounting for the possibility of being behind a proxy.
        """
        ip = environ.get("HTTP_X_FORWARDED_FOR", None)
        if ip:
            # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
            proxies = ip.split(", ") 
            ip = proxies[0]
        else:
            ip = environ.get("REMOTE_ADDR", "")
        return ip

    @staticmethod
    def getFullUri(environ):
        if not environ:
            return ""
        
        path = environ.get("PATH_INFO", None)
        if (path is None) or (len(path) <= 0):
            return ""
        
        query = environ.get("QUERY_STRING", None)
        if (query is None) or (len(query) <= 0):
            return path
        else:
            return "%s?%s" % (path, query)

    @staticmethod
    def resolveResponseObject(obj):
        from bottle import BaseResponse, response
        if isinstance(obj, BaseResponse):
            return obj
        else:
            return response

    @staticmethod
    def getRequestHeadersMapping(args):
        return BottleHttpWeaver.getExtraHeadersMapping(BaseHttpWeaver.REQUEST_HEADER_PREFIX, args.get(BaseHttpWeaver.REQ_HEADERS_CONFIG_PROP, None), True)

    def fillExtraRequestHeaders(self,hdrs,props):
        return BaseHttpWeaver.fillExtraMappedHeaders(hdrs, self.reqHeadersMappings, props)

    @staticmethod
    def getResponseHeadersMapping(args):
        return BottleHttpWeaver.getExtraHeadersMapping(BaseHttpWeaver.RESPONSE_HEADER_PREFIX, args.get(BaseHttpWeaver.RSP_HEADERS_CONFIG_PROP, None), False)

    @staticmethod
    def fillResponseHeaders(headers,mapping,props):
        if (headers is None) or (len(headers) <= 0):
            return props
        if len(mapping) <= 0:
            return props
        if props is None:
            props = {}

        for item in headers:
            name = item[0]
            key = mapping.get(name, None)
            if Helpers.isEmpty(key):
                continue

            value = str(item[1]);
            if Helpers.isEmpty(value):
                continue
            props[key] = value

        return props

    def fillExtraResponseHeaders(self,rsp,props):
        if rsp is None:
            return props
        elif hasattr(rsp, "headerlist"):
            return BottleHttpWeaver.fillResponseHeaders(rsp.headerlist, self.rspHeadersMappings, props)
        else:
            return props

    def __init__(self, logFactory, args, dispatcher):
        super(BottleHttpWeaver,self).__init__("bottle-http", logFactory, args, dispatcher)
        self.reqHeadersMappings = BottleHttpWeaver.getRequestHeadersMapping(args)
        self.rspHeadersMappings = BottleHttpWeaver.getResponseHeadersMapping(args)
        self.BOTTLE_TRACEID_HEADER = BottleHttpWeaver.getMappedHeaderName(BaseHttpWeaver.TRACEID_HEADER)

        from bottle import Bottle, HTTPError
        old_handle = Bottle._handle
        thisWeaver = self

        def _handle(self, environ):
            error = None
            startCorrelation = thisWeaver.startCorrelationContext('bottle', environ.get(thisWeaver.BOTTLE_TRACEID_HEADER, None))
            startTime = BaseWeaver.timestampValue()
            try:
                out = old_handle(self, environ)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()
            endCorrelation = thisWeaver.endCorrelationContext(startCorrelation)

            props = { 
                'objecttype': 'Bottle',
                'function': '_handle',
                'signature': '(self, environ)'
            }
  
            BaseWeaver.setTraceEssenceCorrelation(props, startCorrelation, endCorrelation)
            props = BaseHttpWeaver.fillRequestDetails(props=props,
                                              uri=BottleHttpWeaver.getFullUri(environ),
                                              method=environ.get('REQUEST_METHOD', 'UNKNOWN'),
                                              remoteAddress=BottleHttpWeaver.getRemoteAddress(environ),
                                              remoteUser=environ.get('REMOTE_USER', ""),
                                              userAgent=environ.get('HTTP_USER_AGENT', ""),
                                              requestSize=environ.get('CONTENT_LENGTH', None))
            BaseHttpWeaver.parseProtocol(environ.get("SERVER_PROTOCOL", ""), props)
            thisWeaver.fillExtraRequestHeaders(environ, props)

            # NOTE: in order to access specific header XXXX:
            #
            # 1. HTTP_xxxxx value in the 'environ' argument
            # 2. The 'bottle.request' object in the 'environ' argument (not always there...)
            # 3. The self.headers method result

            rsp = BottleHttpWeaver.resolveResponseObject(out)
            if isinstance(error, HTTPError):
                rsp = error

            statusCode = -1
            contentLength = -1
            if rsp:
                statusCode = rsp.status_code
                contentLength = BaseHttpWeaver.convertSizeValue(rsp.get_header('Content-Length'))
                thisWeaver.fillExtraResponseHeaders(rsp, props)

            if (contentLength <= 0) and (error is None):
                if isinstance(out, (str, unicode)):
                    contentLength = len(out)
            BaseHttpWeaver.fillResponseDetails(props=props, statusCode=statusCode, responseSize=contentLength)
                
            thisWeaver.dispatch(startTime, endTime, props, error)

            if error is None:
                return out
            else:
                raise error

        Bottle._handle = _handle