#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

class Helpers(object):
    @staticmethod
    def isEmpty(s):
        if (s is None) or (len(s) <= 0):
            return True
        else:
            return False

    @staticmethod
    def stripQuotes(s):
        if Helpers.isEmpty(s):
            return s
        
        if len(s) <= 1:
            return s

        if (s[0] == s[-1]) and s.startswith(("'", '"')):
            return s[1:-1]
        else:
            return s

    @staticmethod
    def toSafeString(s):
        if s is None:
            return None
        elif isinstance(s, str):
            return s
        elif isinstance(s, unicode):
            return s.encode('utf-8')
        else:
            return str(s)
