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

class PymongoWeaver(BaseDatabaseWeaver):
    @property
    def VENDOR(self):
        return "mongodb"
    
    def __init__(self, logFactory, args, dispatcher):
        super(PymongoWeaver,self).__init__("mongodb", logFactory, args, dispatcher)

        # see http://api.mongodb.org/python/current/api/pymongo/collection.html
        from pymongo.collection import Collection
        thisWeaver = self

        old_save = Collection.save
        def save(self, to_save, manipulate=True, safe=None, check_keys=True, **kwargs):
            error = None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_save(self, to_save, manipulate=manipulate, safe=safe, check_keys=check_keys, **kwargs)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()

            thisWeaver.handleCollectionOperation(self, "save", BaseWeaver.stringifyArgument(to_save), startTime, endTime, error)

            if error is None:
                return result
            else:
                raise error
        Collection.save = save

        old_insert = Collection.insert        
        def insert(self, doc_or_docs, manipulate=True, safe=None, check_keys=True, continue_on_error=False, **kwargs):
            error = None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_insert(self, doc_or_docs=doc_or_docs, manipulate=manipulate, safe=safe, check_keys=check_keys, continue_on_error=continue_on_error, **kwargs)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()

            thisWeaver.handleCollectionOperation(self, "insert", BaseWeaver.stringifyArgument(doc_or_docs), startTime, endTime, error)

            if error is None:
                return result
            else:
                raise error
        Collection.insert = insert
        
        old_update = Collection.update
        def update(self, spec, document, upsert=False, manipulate=False, safe=None, multi=False, check_keys=True, **kwargs):
            error = None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_update(self, spec, document, upsert=upsert, manipulate=manipulate, safe=safe, multi=multi, check_keys=check_keys, **kwargs)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()

            thisWeaver.handleCollectionOperation(self, "update", BaseWeaver.stringifyArgument((spec, document)), startTime, endTime, error)

            if error is None:
                return result
            else:
                raise error
        Collection.update = update

        old_remove = Collection.remove
        def remove(self, spec_or_id=None, safe=None, multi=True, **kwargs):
            error = None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_remove(self, spec_or_id=spec_or_id, safe=safe, multi=multi, **kwargs)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()

            thisWeaver.handleCollectionOperation(self, "remove", BaseWeaver.stringifyArgument(spec_or_id), startTime, endTime, error)

            if error is None:
                return result
            else:
                raise error
        Collection.remove = remove

        # NOTE: we do not weave 'find_one' since it invokes 'find'      
        old_find = Collection.find
        def find(self, *args, **kwargs):
            error = None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_find(self, *args, **kwargs)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()

            thisWeaver.handleCollectionOperation(self, "find", BaseWeaver.stringifyArgument(*args), startTime, endTime, error)

            if error is None:
                return result
            else:
                raise error
        Collection.find = find

        old_find_and_modify = Collection.find_and_modify            
        def find_and_modify(self, query={}, update=None, upsert=False, sort=None, full_response=False, **kwargs):
            error = None
            startTime = BaseWeaver.timestampValue()
            try:
                result = old_find_and_modify(self, query=query, update=update, upsert=upsert, sort=sort, full_response=full_response, **kwargs)
            except:
                excInfo = sys.exc_info()
                error = excInfo[0]
            endTime = BaseWeaver.timestampValue()

            thisWeaver.handleCollectionOperation(self, "find_and_modify", BaseWeaver.stringifyArgument(query), startTime, endTime, error)

            if error is None:
                return result
            else:
                raise error
        Collection.find = find

    def handleCollectionOperation(self, collection, funcName, funcArgs, startTime, endTime, error):
        collectionName = Helpers.toSafeString(collection.name)

        db = collection.database
        dbName = Helpers.toSafeString(db.name)

        conn = db.connection
        hostName = Helpers.toSafeString(conn.host) or "UNKNOWN"
        portValue = conn.port or -1

        props = { 
                'objecttype': 'pymongo.collection.Collection',
                'function': funcName,
                'signature': '(args)',      # TODO consider using an actual signature (if information is useful in any way)
                'entity': 'COLLECTION',
                'target': collectionName.upper(),
                'host': hostName,
                'port': portValue,
                'db': dbName
            }

        self.prepareQueryProperties(re.sub(r'_', "", funcName), None, startTime, endTime, props, error)

        # fix some value that are not SQL ones
        props['entity'] = 'COLLECTION'
        props['target'] = collectionName.upper()

        # fix some value that are not SQL
        queryArgs = funcArgs
        if queryArgs is None:
            queryArgs = ''
        props['query'] = "%s#%s(%s)" % (collectionName, funcName, queryArgs)

        if self.logger.traceEnabled:
            self.logger.trace("handleCollectionOperation(%s)" % props['query'])

        if self.dispatch(startTime, endTime, props, error):
            return props
        else:
            return None
