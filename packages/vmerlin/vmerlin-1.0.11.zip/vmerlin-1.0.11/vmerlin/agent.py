#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import sys
import os
import json

from .logger import LogFactory
from .sender import HttpCommandSender, ConsoleCommandSender
from .dispatcher import DataDispatcher
from .genericweaver import initWeavers

# ----------------------------------------------------------------------------

def isNumberString(value):
    """
    Checks if value is a string that has only digits - possibly with leading '+' or '-'
    """
    if not value:
        return False
    
    sign = value[0]
    if (sign == '+') or (sign == '-'):
        if len(value) <= 1:
            return False

        absValue = value[1:]
        return absValue.isdigit()
    else:
        if len(value) <= 0:
            return False
        else:
            return value.isdigit()

# ----------------------------------------------------------------------------

def normalizeValue(value):
    """
    Checks if value is 'True', 'False' or all numeric and converts it accordingly
    Otherwise it just returns it
    """
    
    if not value:
        return value

    loCase = value.lower()
    if loCase == "none":
        return None
    elif loCase == "true":
        return True
    elif loCase == "false":
        return False
    elif isNumberString(loCase):
        return int(loCase)
    else:
        return value

# ----------------------------------------------------------------------------

def parseCommandLineArguments(args=None):
    """
    Parses an array of arguments having the format: --name=value. If
    only --name is provided then it is assumed to a TRUE boolean value.
    If the value is all digits, then it is assumed to be a number.
    
    The result is a dictionary with the names as the keys and value
    as their mapped values
    """

    if (args is None) or (len(args) <= 0):
        return {}

    valsMap = {}
    for item in args:
        if not item.startswith("--"):
            raise Exception("Missing option identifier: %s" % item)
        
        propPair = item[2:]     # strip the prefix
        sepPos = propPair.find('=')

        if sepPos == 0:
            raise Exception("Missing name: %s" % item)
        if sepPos >= (len(propPair) - 1):
            raise Exception("Missing value: %s" % item)

        if sepPos < 0:
            valsMap[propPair] = True
        else:
            propName = propPair[0:sepPos]
            propValue = propPair[sepPos + 1:]
            valsMap[propName] = normalizeValue(propValue)

    return valsMap

# ----------------------------------------------------------------------------

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value

    return rv

def readConfigFile(path):
    if not os.path.isfile(path):
        # print "Configuration file not found: %s" % path
        return None
    
    # print "Reading configuration from %s" % path

    configLines = []
    huntForCommendEnd = False

    f = open(path, "r")
    try:
        for jsonLine in f.readlines():
            line = jsonLine.strip(" \t\r\n")

            if len(line) <= 0:
                continue    # skip empty lines
            if line.startswith("//"):
                continue    # skip one line comments
            
            if line.startswith("/*"):
                huntForCommendEnd = True
                # fall through in case same line start/end of comment
            
            if huntForCommendEnd:
                if line.endswith("*/"):
                    huntForCommendEnd = False
                continue
            
            configLines.append(jsonLine)
    finally:
        f.close()
    
    if huntForCommendEnd:
        raise Exception("Imbalanced comment in file=%s" % path)

    jsonData = "".join(configLines)
    # see http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
    return json.loads(jsonData, object_hook=_decode_dict)

# ----------------------------------------------------------------------------
    
def readDefaultConfigFile():
    thisModulePath = os.path.abspath(__file__)
    thisModuleFolder = os.path.dirname(thisModulePath)
    return readConfigFile(os.path.join(thisModuleFolder, "config", "config.defaults.json"))
    
# ----------------------------------------------------------------------------

def readUserConfigConfigFile(args=None):
    if (len(args) > 0) and 'config-file' in args:
        return readConfigFile(args['config-file'])
    
    candidates = [ ]
    cwd = os.path.abspath(os.getcwd())
    pathScript = sys.argv[0]
    if len(pathScript) > 0:
        pathScript = os.path.abspath(pathScript)
        pathScript = os.path.dirname(pathScript)
        if pathScript != cwd:
            candidates.append(pathScript)
    
    # prefer path script over CWD
    candidates.append(cwd)
    for basePath in candidates:
        filePath = os.path.join(basePath, 'vmerlin.config.json')
        # print "Checking %s" % filePath
        if os.path.isfile(filePath):
            return readConfigFile(filePath)

    # print "No user configuration file found"
    return None

# ----------------------------------------------------------------------------

def mergeConfiguration(src, dst):
    if src is None:
        return dst
    if dst is None:
        return src

    for name,value in src.items():
        if name in dst:
            override = dst[name]
            if isinstance(override, dict):
                mergeConfiguration(value, override)
                continue

            if value == override:
                continue

            # print "- Override %s[%s] => %s" % (name, str(override), str(value))

        dst[name] = value
    
    return dst

# ----------------------------------------------------------------------------

def getConfigSection(config, *args):
    if (config is None) or (len(args) <= 0):
        return {}
    
    for section in args:
        if not section in config:
            return {}
        config = config[section]
    
    return config

# ============================================================================

def resolveCommandSender(logFactory, args):
    senderType = args.get("commands-sender", "http")
    if "http" == senderType:
        return HttpCommandSender(logFactory, getConfigSection(args, "transport", "http"))
    elif "console" == senderType:
        return ConsoleCommandSender(logFactory, args)
    else:
        raise ValueError("Unknown commands sender type: %s" % senderType)

def initAgent(args=None):
    args = parseCommandLineArguments(args)
    defaultArgs = readDefaultConfigFile()
    userArgs = readUserConfigConfigFile(args)
    configArgs = mergeConfiguration(userArgs, defaultArgs)
    
    # if agent disabled, then do nothing
    if not configArgs.get("enabled", True):
        return

    logFactory = LogFactory(getConfigSection(configArgs, "logger"))
    logger = logFactory.getLogger("vMerlinAgent")

    commandSender = resolveCommandSender(logFactory, configArgs)
    logger.info("Using %s" % commandSender.__class__.__name__)
    dispatcher = DataDispatcher(logFactory, commandSender, getConfigSection(configArgs, "dispatcher"))

    logger.info("Starting %s" % dispatcher.__class__.__name__)
    try:
        dispatcher.daemon = True
        dispatcher.start()
    except Exception as err:
        logger.error("%s exited - %s: %s" % (dispatcher.__class__.__name__, err.__class__.__name__, str(err)), err)
        raise err

    initWeavers(logger, logFactory, getConfigSection(configArgs, "weavers"), dispatcher)