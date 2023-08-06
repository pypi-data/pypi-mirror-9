#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import sys
import re

from .genericweaver import BaseWeaver
from .dbweaver import BaseDatabaseWeaver
from .helpers import Helpers

class RedisWeaver(BaseDatabaseWeaver):
    @property
    def VENDOR(self):
        return "redis"
    
    def __init__(self, logFactory, args, dispatcher):
        super(RedisWeaver,self).__init__("redis", logFactory, args, dispatcher)
        
        from redis import Connection
        thisWeaver = self
    
        old_connect = Connection.connect
        def connect(self):
            error = None
            connecting = self._sock is None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_connect(self)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()
            
            if connecting:
                thisWeaver.handleConnectionEvent(self, "connect", "open", startTime, endTime, error)

            if error is None:
                return result
            else:
                raise error
        Connection.connect = old_connect

        old_disconnect = Connection.disconnect
        def disconnect(self):
            error = None
            disconnecting = self._sock is not None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_disconnect(self)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()
            
            if disconnecting:
                thisWeaver.handleConnectionEvent(self, "disconnect", "close", startTime, endTime, error)

            if error is None:
                return result
            else:
                raise error
        Connection.disconnect = disconnect

        old_send_command = Connection.send_command
        def send_command(self, *args):
            error = None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_send_command(self, *args)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()

            command_name = args[0]
            if len(args) > 1:
                command_target = BaseWeaver.stringifyArgument(args[1])
                command = ' '.join(args)
            else:
                command_target = 'STORE'
                command = command_name
            thisWeaver.handleExecutedCommand(self, command_name, command_target, BaseWeaver.stringifyArgument(command), startTime, endTime, error)

            if error is None:
                return result
            else:
                raise error
        Connection.send_command = send_command

    def handleConnectionEvent(self, conn, funcName, action, startTime, endTime, error):
        hostName = Helpers.toSafeString(conn.host) or "UNKNOWN"
        portValue = conn.port or -1
        dbName = Helpers.toSafeString(str(conn.db))

        props = { 
            'objecttype': 'Connection',
            'function': funcName,
            'signature': '()' 
        }

        if self.dispatchConnection(action, hostName, portValue, dbName, startTime, endTime, props, error):
            return props
        else:
            return None

    def handleExecutedCommand(self, conn, funcName, targetName, command, startTime, endTime, error):
        hostName = Helpers.toSafeString(conn.host) or "UNKNOWN"
        portValue = conn.port or -1
        dbName = Helpers.toSafeString(str(conn.db))

        props = { 
                'objecttype': 'redis.Connection',
                'function': 'send_command',
                'signature': '(args)',
                'target': targetName,
                'host': hostName,
                'port': portValue,
                'db': dbName
            }
        self.prepareQueryProperties(re.sub(r'_', "", funcName), None, startTime, endTime, props, error)

        # fix some value that are not SQL ones
        props['target'] = targetName.upper()
        props['entity'] = 'STORE'
        props['query'] = command

        if self.logger.traceEnabled:
            self.logger.trace("handleExecutedCommand(%s)" % props['query'])

        if self.dispatch(startTime, endTime, props, error):
            return props
        else:
            return None
