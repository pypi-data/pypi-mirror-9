#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import sys

from .genericweaver import BaseWeaver
from .dbweaver import BaseDatabaseWeaver

class MySQLdbWeaver(BaseDatabaseWeaver):
    @property
    def VENDOR(self):
        return "mysql"

    @staticmethod
    def extractConnectionDatabaseDetails(conn, props):
        if conn is None:
            return props
        
        if hasattr(conn, 'host'):
            props['host'] = conn.host
        if hasattr(conn, 'port'):
            props['port'] = conn.port
        if hasattr(conn, 'db'):
            props['db'] = conn.db
        return props

    @staticmethod
    def extractCursorDatabaseDetails(cursor, props):
        if cursor is None:
            return props
        if not hasattr(cursor, 'connection'):
            return props
        else:
            return MySQLdbWeaver.extractConnectionDatabaseDetails(cursor.connection, props)

    def __init__(self, logFactory, args, dispatcher):
        super(MySQLdbWeaver,self).__init__("mysql", logFactory, args, dispatcher)

        import MySQLdb
        # see http://mysql-python.sourceforge.net/MySQLdb-1.2.2/public/MySQLdb.cursors.BaseCursor-class.html
        old_execute = MySQLdb.cursors.BaseCursor.execute
        thisWeaver = self

        def execute(self, query, args=None):
            error = None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_execute(self, query, args)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()

            props = { 
                'objecttype': 'MySQLdb.cursors.BaseCursor',
                'function': 'execute',
                'signature': '(string, args)' 
            }
            
            MySQLdbWeaver.extractCursorDatabaseDetails(self, props)
            thisWeaver.dispatchQuery(query, args, startTime, endTime, props, error)

            if error is None:
                return result
            else:
                raise error

        MySQLdb.cursors.BaseCursor.execute = execute
        
        old_connect = MySQLdb.connect
        def connect(*args, **kwargs):
            # see http://mysql-python.sourceforge.net/MySQLdb-1.2.2/public/MySQLdb.connections.Connection-class.html#__init__
            host = kwargs.get("host", None)
            port = kwargs.get("port", -1)
            db = kwargs.get("db", None)
            error = None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_connect(*args, **kwargs)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()

            props = { 
                'objecttype': 'Connection',
                'function': 'connect',
                'signature': '(*args, **kwargs)' 
            }

            thisWeaver.dispatchConnection("open", host, port, db, startTime, endTime, props, error)
            
            if error is None:
                # mark the data into the connection so it is available to the executor
                if not hasattr(result, 'host'):
                    result.host = host
                if not hasattr(result, 'port'):
                    result.port = port
                if not hasattr(result, 'db'):
                    result.db = db
    
                return result
            else:
                raise error
        MySQLdb.connect = connect

            