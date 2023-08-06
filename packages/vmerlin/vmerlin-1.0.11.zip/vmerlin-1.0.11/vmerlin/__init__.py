#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import sys

pyVersion = sys.version_info
if pyVersion.major != 2:
    raise ValueError("Major Python version must be 2.x: %s" % str(pyVersion))
if pyVersion.minor < 7:
    print "Warning: minor Python version %s should be at least 2.7+" % str(pyVersion)
