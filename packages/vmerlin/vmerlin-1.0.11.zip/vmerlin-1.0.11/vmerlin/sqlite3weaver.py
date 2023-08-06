#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import sys

from .genericweaver import BaseWeaver
from .dbweaver import BaseDatabaseWeaver

class Sqlite3Weaver(BaseDatabaseWeaver):
    @property
    def VENDOR(self):
        return "sqlite3"

    @staticmethod
    def extractConnectionDatabaseDetails(conn, props):
        if conn is None:
            return props

        # TODO find a way to extract the database name
        # NOTE: wrapping sqlite3.connect does not help - for some reason the function is not invoked
        props['host'] = 'file'
        props['port'] = 0
        props['database'] = 'sqlite3'
        return props

    @staticmethod
    def extractCursorDatabaseDetails(cursor, props):
        if cursor is None:
            return props
        if not hasattr(cursor, 'connection'):
            return props
        else:
            return Sqlite3Weaver.extractConnectionDatabaseDetails(cursor.connection, props)
    
    def __init__(self, logFactory, args, dispatcher):
        super(Sqlite3Weaver,self).__init__("sqlite3", logFactory, args, dispatcher)
        
        thisWeaver = self
        import sqlite3
        from forbiddenfruit import curse

        old_execute = sqlite3.Cursor.execute
        def execute(self, sql, params=None):
            if params is None:  # avoid ValueError by the binary function
                params = ()

            error = None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_execute(self, sql, params)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()

            props = { 
                'objecttype': 'sqlite3.Cursor',
                'function': 'execute',
                'signature': '(string, params)' 
            }

            Sqlite3Weaver.extractCursorDatabaseDetails(self, props)
            thisWeaver.dispatchQuery(sql, args, startTime, endTime, props, error)

            if error is None:
                return result
            else:
                raise error
        curse(sqlite3.Cursor, "execute", execute)