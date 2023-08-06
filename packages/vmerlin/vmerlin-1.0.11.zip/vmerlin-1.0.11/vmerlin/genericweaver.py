#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import time
import string
import re
import threading

from .logger import LoggingClass
from .helpers import Helpers
from array import array

# ----------------------------------------------------------------------------

class BaseWeaver(LoggingClass):
    def __init__(self, flavor, logFactory, args, dispatcher):
        super(BaseWeaver,self).__init__(logFactory, args)
        self.flavor = flavor
        self.dispatcher = dispatcher

    @staticmethod
    def stringifyArgument(argVal, maxLen=140):
        if argVal is None:
            return "None"
        elif (maxLen <= 0):
            return ""
        elif isinstance(argVal, str):
            strValue = filter(lambda x: x in string.printable, argVal)
            strValue = re.sub(r'\s', " ", strValue)
            strValue = re.sub(r'[ ]+', " ", strValue)
            strValue = strValue.strip(" ")

            if len(strValue) > maxLen:
                return strValue[0:maxLen]
            else:
                return strValue
        elif isinstance(argVal, unicode):
            return BaseWeaver.stringifyArgument(argVal.encode('utf-8'), maxLen)
        elif isinstance(argVal, (int, long, float )):
            return BaseWeaver.stringifyArgument(str(argVal), maxLen)
        elif isinstance(argVal, (tuple, list, array)):
            if len(argVal) <= 0:
                return "()"
            
            remLen = maxLen
            str_list = []
            for value in argVal:
                if remLen <= 0:
                    break

                strval = BaseWeaver.stringifyArgument(value, remLen)
                slen = len(strval)
                if slen <= 0:
                    continue
                str_list.append(strval)
                remLen = remLen - slen
            
            return '(%s)' % BaseWeaver.stringifyArgument(', '.join(str_list), maxLen)
        elif isinstance(argVal, dict):
            if len(argVal) <= 0:
                return "{}"

            remLen = maxLen
            str_list = []
            for key,value in argVal.items():
                if remLen <= 0:
                    break
                
                keyValue = BaseWeaver.stringifyArgument(key, remLen)
                keyLen = len(keyValue)
                remLen = remLen - keyLen
                mapValue = BaseWeaver.stringifyArgument(value, remLen)
                mapLen = len(mapValue)
                remLen = remLen - mapLen
                str_list.append("%s: %s" % (keyValue, mapValue))

            return "{ %s }" % BaseWeaver.stringifyArgument(', '.join(str_list), maxLen)
        else:
            return BaseWeaver.stringifyArgument(str(argVal), maxLen)
            
    @staticmethod
    def normalizeErrorText(err=None):
        if err is None:
            return ""
    
        errorText = Helpers.toSafeString(str(err))
        textLen = len(errorText)
        if textLen > 0:
            if textLen > 140:
                errorText = errorText[0:140]
        else:
            errorText = "Error"
        return errorText

    threadLocal = threading.local()

    def startCorrelationContext(self, context="weaving", value=None):
        correlation = getattr(BaseWeaver.threadLocal, 'correlation', None)

        if Helpers.isEmpty(correlation):
            if Helpers.isEmpty(value):
                correlation = self.dispatcher.generateCorrelationId(context)
            else:
                correlation = value
            BaseWeaver.threadLocal.correlation = correlation

        return correlation

    @staticmethod
    def getCorrelationContext():
        return getattr(BaseWeaver.threadLocal, 'correlation', None)

    def endCorrelationContext(self, context=None):
        correlation = getattr(BaseWeaver.threadLocal, 'correlation', None)
        if (correlation is None) or (len(correlation) <= 0):
            return correlation
        
        if (not context is None) and (len(context) > 0):
            if correlation != context:
                return correlation

        if (not correlation is None) and (len(correlation) > 0):
            BaseWeaver.threadLocal.correlation = None

        return correlation

    @staticmethod
    def resolveCorrelationContent(startCorrelation, endCorrelation):
        if Helpers.isEmpty(startCorrelation):
            return endCorrelation
        else:
            return startCorrelation
    
    @staticmethod
    def setTraceEssenceCorrelation(props, startCorrelation, endCorrelation):
        correlation = BaseWeaver.resolveCorrelationContent(startCorrelation, endCorrelation)
        if not Helpers.isEmpty(correlation):
            props['correlation'] = correlation
        return correlation

    def dispatch(self, startTime, endTime, props, error=None):
        if not 'flavor' in props:
            props['flavor'] = self.flavor

        if not 'datetime' in props:
            localtime = time.gmtime(startTime)
            props['datetime'] = "{date:yyyy-MM-dd'T'HH:mm:ss.SSSZ}%s" % time.strftime("%Y-%m-%dT%H:%M:%S.000Z", localtime)

        # check if within a weaving context
        if not 'correlation' in props:
            correlation = BaseWeaver.getCorrelationContext()
            if not Helpers.isEmpty(correlation):
                props['correlation'] = correlation

        nanos = BaseWeaver.nanosDiff(startTime, endTime)
        props['nanoseconds'] = nanos
        props['duration'] =  BaseWeaver.nanosToMillis(nanos)
        props['error'] = BaseWeaver.normalizeErrorText(error)
                    
        return self.dispatcher.addItem(props)

    @staticmethod
    def timestampValue():
        return time.time()
    
    @staticmethod
    def nanosDiff(startTime, endTime):
        diffTime = endTime - startTime
        if diffTime < 0:
            diffTime = 0 - diffTime
        return (int) (round(diffTime * 1000000000))
    
    @staticmethod
    def nanosToMillis(nanos):
        return (int) (round(nanos / 1000000))

    @staticmethod
    def millisDiff(startTime, endTime):
        diffTime = endTime - startTime
        if diffTime < 0:
            diffTime = 0 - diffTime
        return (int) (diffTime * 1000)

    @staticmethod
    def putIfValidString(props, key, value):
        if (props is None) or (value is None):
            return props
        
        value = Helpers.toSafeString(value)
        if len(value) > 0:
            props[key] = value
        return props

    @staticmethod
    def isValidIPv4AddressComponent(c):
        if Helpers.isEmpty(c):
            return False
        
        if (not c.isdigit()) or (len(c) > 3):
            return False

        value = int(c)
        if (value < 0) or (value > 255):
            return False
        else:
            return True
        
    @staticmethod
    def isIPv4Address(addr):
        if Helpers.isEmpty(addr):
            return False
        
        comps = addr.split('.')
        if len(comps) != 4:
            return False
        
        for c in comps:
            if not BaseWeaver.isValidIPv4AddressComponent(c):
                return False

        return True

    @staticmethod
    def isIPv4LoopbackAddress(addr):
        if Helpers.isEmpty(addr):
            return False
        
        # check most likely values
        if (addr == 'localhost') or (addr == '127.0.0.1'):
            return True

        comps = addr.split('.')
        numComps = len(comps)
        if numComps != 4:
            return False
        
        for index in range(numComps):
            c = comps[index]
            if not BaseWeaver.isValidIPv4AddressComponent(c):
                return False

            if index == 0:  # 127.x.y.z
                value = int(c)
                if value != 127:
                    return False

        return True

    @staticmethod
    def getEmbeddedIPv4Address(addr):
        if Helpers.isEmpty(addr):
            return addr

        # check if embedded IPv4
        pos = addr.find(":", -1)
        if (pos <= 0) or (pos >= (len(addr) - 1)):
            return None
        
        addr = addr[pos + 1:]
        # remove mask bits length
        pos = addr.find('/')
        if pos > 0:
            addr = addr[0:pos]
        
        if BaseWeaver.isIPv4Address(addr):
            return addr
        else:
            return None

    @staticmethod
    def isIPv6LoopbackAddress(addr):
        if Helpers.isEmpty(addr):
            return False
        
        # check most likely values
        if (addr == '::1') or (addr == '::1/128') or (addr == "0:0:0:0:0:0:0:1"):
            return True

        addr = BaseWeaver.getEmbeddedIPv4Address(addr)
        if BaseWeaver.isIPv4LoopbackAddress(addr):
            return True
        else:
            return False

    @staticmethod
    def sanitizeRemoteAddress(addr):
        if Helpers.isEmpty(addr):
            return ""

        if BaseWeaver.isIPv4Address(addr):
            return addr
        
        if BaseWeaver.isIPv6LoopbackAddress(addr):
            return "127.0.0.1";

        addr = BaseWeaver.getEmbeddedIPv4Address(addr)
        if BaseWeaver.isIPv4Address(addr):
            return addr
        else:
            return "";

# ----------------------------------------------------------------------------

def initWeavers(logger, logFactory, args, dispatcher):
    weavers = []
    for name, config in args.items():
        enabled = config.get("enabled", False)
        if not enabled:
            if logger.debugEnabled:
                logger.debug("initWeavers(%s) - skip [disabled]" % name)
            continue
        
        weaverConfig = config.get("configuration", None)
        if weaverConfig is None:
            weaverConfig = {}

        try:    # TODO find some reflective way to do this
            if name == 'mysql':
                from .mysqlweaver import MySQLdbWeaver
                weaver = MySQLdbWeaver(logFactory, weaverConfig, dispatcher)
            elif name == 'django':
                from .djangoweaver import DjangoHttpWeaver
                weaver = DjangoHttpWeaver(logFactory, weaverConfig, dispatcher)
            elif name == 'sqlite3':
                from .sqlite3weaver import Sqlite3Weaver
                weaver = Sqlite3Weaver(logFactory, weaverConfig, dispatcher)
            elif name == 'tornado':
                from .tornadoweaver import TornadoHttpWeaver
                weaver = TornadoHttpWeaver(logFactory, weaverConfig, dispatcher)
            elif name == 'pymongo':
                from .pymongoweaver import PymongoWeaver
                weaver = PymongoWeaver(logFactory, weaverConfig, dispatcher)
            elif name == 'redis':
                from .redisweaver import RedisWeaver
                weaver = RedisWeaver(logFactory, weaverConfig, dispatcher)
            elif name == 'bottle':
                from .bottleweaver import BottleHttpWeaver
                weaver = BottleHttpWeaver(logFactory, weaverConfig, dispatcher)
            else:
                raise ValueError("Unknown weaver type")

            if logger.debugEnabled:
                logger.debug("initWeavers(%s) - initialized: %s" % (name, weaver.__class__.__name__))
            weavers.append(weaver)
        except Exception as err:
            logger.warning("initWeavers(%s) Failed (%s) to initialize: %s" % (name, err.__class__.__name__, str(err)), err)

    return weavers