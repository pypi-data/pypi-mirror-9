#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import re

from .genericweaver import BaseWeaver
from .helpers import Helpers

# ----------------------------------------------------------------------------

class BaseDatabaseWeaver(BaseWeaver):
    def __init__(self, flavor, logFactory, args, dispatcher):
        super(BaseDatabaseWeaver,self).__init__(flavor, logFactory, args, dispatcher)

    @staticmethod
    def createDatabaseAccessURL(vendor, hostName, portValue, databaseName):
        return "%s://%s:%s?%s" % (vendor.lower(), hostName, str(portValue), databaseName)

    @staticmethod
    def createDatabaseAccessURLFromProps(vendor, props):
        return BaseDatabaseWeaver.createDatabaseAccessURL(vendor, props.get("host", "0.0.0.0"), props.get("port", -1), props.get("db", "unknown"))

    # removes any quotes, braces, brackets, etc.
    @staticmethod
    def normalize(s):
        s = Helpers.stripQuotes(s)
        if Helpers.isEmpty(s):
            return s

        # handle case of function call: name(...)
        for index in range(len(s)):
            ch = s[index]

            if (ch >= 'A') and (ch <= 'Z'):
                continue
            if (ch >= 'a') and (ch <= 'z'):
                continue
            if (ch >= '0') and (ch <= '9'):
                continue
            if ch in '-_':
                continue

            return s[0:index].upper()

        return s.upper();

    @staticmethod
    def targetAfterVerb(props, comps, startIndex, value):
        numComps = len(comps)

        for index in range(numComps):
            compValue = comps[index]
            verb = compValue.upper()
            if verb == value:
                index += 1
                if index < numComps:
                    props['target'] = BaseDatabaseWeaver.normalize(comps[index]);
                    break

        return props;

    @staticmethod
    def targetAfterKeywords(props, comps, startIndex, keywords):
        index = startIndex
        numComps = len(comps)

        while index < numComps:
            candidate = comps[index].upper()

            if not candidate in keywords:
                props['target'] = BaseDatabaseWeaver.normalize(candidate)
                break

            index += 1

        return props;

    KNOWN_ENTITIES = (
            # some known entities
            "TABLE", "INDEX", "VIEW", "DATABASE", "SCHEMA", "USER", "SEQUENCE", "CONSTRAINT",
            # see http://dev.mysql.com/doc/refman/5.1/en/sql-syntax-data-definition.html
            "EVENT", "LOGFILE", "FUNCTION", "PROCEDURE", "SERVER", "TABLESPACE", "TRIGGER",
            # see http://www.postgresql.org/docs/9.3/static/sql-commands.html
            "AGGREGATE", "CAST", "COLLATION", "CONVERSION", "EXTENSION", "DOMAIN",
            "WRAPPER", "GROUP", "LANGUAGE", "OPERATOR", "ROLE", "RULE", "TYPE", "TEXT",
            # see http://www.hsqldb.org/doc/guide/ch09.html
            "ALIAS",
            # see http://infocenter.sybase.com/archive/topic/com.sybase.infocenter.dc38151.1260/html/iqref/X201293.htm    \
            "SERVICE", "DBSPACE", "MESSAGE", "VARIABLE",
            # see http://msdn.microsoft.com/en-us/library/cc879262.aspx
            "ASSEMBLY", "CERTIFICATE", "CONTRACT", "CREDENTIAL", "ENDPOINT",
            "FEDERATION", "LOGIN", "QUEUE", "ROUTE", "STATISTICS", "SYNONYM"
            # TODO add support for 2+ words types - e.g. APPLICATION ROLE, REMOTE SERVICE BINDING, etc.
        )

    @staticmethod
    def locateEntityType(comps, startIndex):
        index = startIndex
        numComps = len(comps)
        while index < numComps:
            entity = comps[index].upper()
            if entity in BaseDatabaseWeaver.KNOWN_ENTITIES:
                return index

        return (-1)

    MODIFIER_KEYWORDS = ( "IF", "NOT", "EXISTS" )

    @staticmethod
    def targetAfterModifier(props, comps):
        entityIndex = BaseDatabaseWeaver.locateEntityType(comps, 1)
        if entityIndex <= 0:
            kwdIndex = 1
        else:
            kwdIndex = entityIndex

        BaseDatabaseWeaver.targetAfterKeywords(props, comps, kwdIndex, BaseDatabaseWeaver.MODIFIER_KEYWORDS)

        if entityIndex > 0:
            props['entity'] = comps[entityIndex].upper()

        return props;

    UPDATE_KEYWORDS = ( "LOW_PRIORITY", "IGNORE", "ONLY" )   # see MySQL, Oracle, Postgres

    QueryTraceEssenceSqlUpdater = {
       'select': lambda props,comps: BaseDatabaseWeaver.targetAfterVerb(props, comps, 2, 'FROM'),
       'insert': lambda props,comps: BaseDatabaseWeaver.targetAfterVerb(props, comps, 1, 'INTO'),
       'delete': lambda props,comps: BaseDatabaseWeaver.targetAfterVerb(props, comps, 1, 'FROM'),
       'update': lambda props,comps: BaseDatabaseWeaver.targetAfterKeywords(props, comps, 1, BaseDatabaseWeaver.UPDATE_KEYWORDS),
       'create': lambda props,comps: BaseDatabaseWeaver.targetAfterModifier(props, comps),
       'alter' : lambda props,comps: BaseDatabaseWeaver.targetAfterModifier(props, comps),
       'drop' :  lambda props,comps: BaseDatabaseWeaver.targetAfterModifier(props, comps)
    }

    @staticmethod
    def normalizeSqlQuery(sql):
        sql = Helpers.toSafeString(sql)
        if len(sql) <= 0:
            return sql
        
        sql = re.sub(r'\s', " ", sql)
        sql = re.sub(r'[ ]+', " ", sql)
        sql = sql.strip(" ")
        return sql
        
    @staticmethod
    def updateSqlEssenceValues(props, sql):
        sql = BaseDatabaseWeaver.normalizeSqlQuery(sql)
        if (props is None) or (len(sql) <= 0):
            return props

        props['query'] = sql

        comps = sql.split(" ")
        numComps = len(comps)
        for index in range(numComps):
            comps[index] = comps[index].strip()

        action = comps[0]
        props['action'] = action.upper()

        key = action.lower()
            
        if key in BaseDatabaseWeaver.QueryTraceEssenceSqlUpdater:
            props['entity'] = 'TABLE'  # assumed as default since this is the most common accessed entity type
            cb = BaseDatabaseWeaver.QueryTraceEssenceSqlUpdater[key]
            cb(props, comps)
        elif numComps > 1:   # for unknown actions assume 2nd argument is target
            props['target'] = BaseDatabaseWeaver.normalize(comps[1]);

        return props

    @staticmethod
    def createSQLLabel(vendor, props):
        action = props['action']
        if 'target' in props:
            target = props['target']
            return "%s %s(%s)" % (vendor.upper(), action, target)
        else:
            return "%s %s" % (vendor.upper(), action)

    @property
    def VENDOR(self):
        raise NotImplementedError("Should have implemented %s#VENDOR" % self.__class__.__name__)

    @VENDOR.setter
    def VENDOR(self, value):
        raise NotImplementedError("Not allowed to change value of vendor property")

    def prepareQueryProperties(self, query, args, startTime, endTime, props=None, error=None):
        if (not args is None) and (len(args) > 0):
            query = query % args

        if props is None:
            props = {}

        props['flavor'] = 'database'
        props['vendor'] = self.VENDOR.lower()
        props['url'] = BaseDatabaseWeaver.createDatabaseAccessURLFromProps(self.VENDOR, props)

        BaseDatabaseWeaver.updateSqlEssenceValues(props, query)
        props['label'] = BaseDatabaseWeaver.createSQLLabel(self.VENDOR, props)

        if self.logger.traceEnabled:
            self.logger.trace("Executed query='%s [%s] in %d nanos" % (props['label'], props['query'], BaseWeaver.nanosDiff(startTime, endTime)))
        return props

    def dispatchQuery(self, query, args, startTime, endTime, props=None, error=None):
        props = self.prepareQueryProperties(query, args, startTime, endTime, props, error)
        if self.dispatch(startTime, endTime, props, error):
            return props
        else:
            return None

    @staticmethod
    def createConnectionEssenceLabel(vendor, action, url):
        return "%s %s CONNECTION TO %s" % (vendor.upper(), action.upper(), url)

    def dispatchConnection(self, action, host, port, db, startTime, endTime, props=None, error=None):
        if props is None:
            props = {}

        host = Helpers.toSafeString(host)
        db = Helpers.toSafeString(db)
        url = BaseDatabaseWeaver.createDatabaseAccessURL(self.VENDOR, host, port, db)
        label = BaseDatabaseWeaver.createConnectionEssenceLabel(self.VENDOR, action, url)

        if self.logger.traceEnabled:
            self.logger.trace("%s in %d nanos" % (label, BaseWeaver.nanosDiff(startTime, endTime)))

        props['flavor'] = 'dbconns'
        props['action'] = action.lower()
        props['vendor'] = self.VENDOR.lower()
        props['host'] = host
        props['port'] = port
        props['db'] = db
        props['url'] = url
        props['label'] = label

        if self.dispatch(startTime, endTime, props, error):
            return props
        else:
            return None
