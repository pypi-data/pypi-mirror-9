#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import sys

from .helpers import Helpers
from .genericweaver import BaseWeaver
from .httpweaver import BaseHttpWeaver

class DjangoHttpWeaver(BaseHttpWeaver):
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
                key = DjangoHttpWeaver.getMappedHeaderName(name)
            if Helpers.isEmpty(key):
                continue
            mapping[key] = BaseHttpWeaver.getMappedHeaderName(prefix, name)

        return mapping

    @staticmethod
    def getRemoteAddress(request):
        """
        Returns the IP of the request, accounting for the possibility of being behind a proxy.
        See https://djangosnippets.org/snippets/2575/
        """
        ip = request.META.get("HTTP_X_FORWARDED_FOR", None)
        if ip:
            # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
            proxies = ip.split(", ") 
            ip = proxies[0]
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip

    @staticmethod
    def getRequestHeadersMapping(args):
        return DjangoHttpWeaver.getExtraHeadersMapping(BaseHttpWeaver.REQUEST_HEADER_PREFIX, args.get(BaseHttpWeaver.REQ_HEADERS_CONFIG_PROP, None), True)

    def fillExtraRequestHeaders(self,hdrs,props):
        return BaseHttpWeaver.fillExtraMappedHeaders(hdrs, self.reqHeadersMappings, props)

    @staticmethod
    def getResponseHeadersMapping(args):
        return DjangoHttpWeaver.getExtraHeadersMapping(BaseHttpWeaver.RESPONSE_HEADER_PREFIX, args.get(BaseHttpWeaver.RSP_HEADERS_CONFIG_PROP, None), False)

    def fillExtraResponseHeaders(self,hdrs,props):
        return BaseHttpWeaver.fillExtraMappedHeaders(hdrs, self.rspHeadersMappings, props)

    def __init__(self, logFactory, args, dispatcher):
        super(DjangoHttpWeaver,self).__init__("django-http", logFactory, args, dispatcher)
        self.reqHeadersMappings = DjangoHttpWeaver.getRequestHeadersMapping(args)
        self.rspHeadersMappings = DjangoHttpWeaver.getResponseHeadersMapping(args)
        self.DJANGO_TRACEID_HEADER = DjangoHttpWeaver.getMappedHeaderName(BaseHttpWeaver.TRACEID_HEADER)

        from django.core.handlers.base import BaseHandler
        from django.http.response import HttpResponseBase

        old_get_response = BaseHandler.get_response
        thisWeaver = self

        def get_response(self, request):
            '''
            Returns an HttpResponse object for the given django.http.request (HttpRequest)
            '''
            error = None
            startCorrelation = thisWeaver.startCorrelationContext('django', request.META.get(thisWeaver.DJANGO_TRACEID_HEADER, None))
            startTime = BaseWeaver.timestampValue()
            try:
                response = old_get_response(self, request)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()
            endCorrelation = thisWeaver.endCorrelationContext(startCorrelation)

            props = { 
                'objecttype': 'django.core.handlers.base.BaseHandler',
                'function': 'get_response',
                'signature': '(self, request)'
            }

            BaseWeaver.setTraceEssenceCorrelation(props, startCorrelation, endCorrelation)

            # see https://docs.djangoproject.com/en/dev/ref/request-response/
            props = BaseHttpWeaver.fillRequestDetails(props=props,
                                              uri=request.get_full_path(),
                                              method=request.META.get('REQUEST_METHOD', 'UNKNOWN'),
                                              remoteAddress=DjangoHttpWeaver.getRemoteAddress(request),
                                              remoteUser=request.META.get('REMOTE_USER', ""),
                                              userAgent=request.META.get('HTTP_USER_AGENT', ""),
                                              requestSize=request.META.get('CONTENT_LENGTH', None))
            thisWeaver.fillExtraRequestHeaders(request.META, props)
            props['protocol'] = request.scheme.upper()

            rsp = response
            if isinstance(error, HttpResponseBase):
                rsp = error
            if isinstance(rsp, HttpResponseBase):
                thisWeaver.fillExtraResponseHeaders(rsp, props)
                BaseHttpWeaver.fillResponseDetails(props=props, statusCode=rsp.status_code, responseSize=rsp.get('Content-Length', None))
            thisWeaver.dispatch(startTime, endTime, props, error)

            if error is None:
                return response
            else:
                raise error
        
        BaseHandler.get_response = get_response
        
