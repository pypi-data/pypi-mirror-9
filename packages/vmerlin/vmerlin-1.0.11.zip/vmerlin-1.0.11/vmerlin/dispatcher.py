#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import os
import sys
import time
import random
import socket
import json
import threading

from .version import __version__

class DataDispatcher(threading.Thread):
    @staticmethod
    def resolveHostId(args):
        host = os.environ.get("VMERLIN_AGENT_HOSTID", None)
        if (host is None) or (len(host) <= 0):
            host = args.get("hostid", None)

        if (host is None) or (len(host) <= 0):
            host = socket.gethostname()

        if (host is None) or (len(host) <= 0):
            return "localhost"
        else:
            return host
    
    @staticmethod
    def resolveAgentId(args, defaultValue):
        agentId = args.get("agentid", defaultValue)
        if len(agentId) <= 0:
            return defaultValue
        else:
            return agentId

    @staticmethod
    def isLocalhost(name):
        if (name is None) or (len(name) <= 0):
            return False

        name = name.lower()
        # TODO makes sure all 127.x.x.x are detected as local host 
        if (name == "localhost") or (name == "127.0.0.1"):
            return True

        # TODO add detection of IPv7 loopback addresses
        return False

    @staticmethod
    def resolveServerLabel(args, hostId, agentId):
        label = args.get("serverLabel", hostId)
        if (label is None) or (len(label) <= 0):
            label = hostId
        
        # TODO find all primary network interfaces and return 1st non-localhost IPv4 address
        if DataDispatcher.isLocalhost(label):
            label = hostId

        return label
    
    @staticmethod
    def resolveApplicationName(appName):
        if (not appName is None) and (len(appName) > 0):
            return appName
        
        pathScript = sys.argv[0]
        if len(pathScript) > 0:
            pathScript = os.path.dirname(pathScript)
            pathScript = os.path.basename(pathScript)

        if len(pathScript) > 0:
            return pathScript
        else:
            return "unknown"

    def __init__(self, logFactory, commandSender, args):
        super(DataDispatcher,self).__init__()
        self.logger = logFactory.getLogger(self.__class__.__name__)
        self.maxItems = args.get("maxPendingItems", 255)
        self.flushInterval = args.get("pendingFlushInterval", 15)
        self.syncResourceInterval = args.get("syncResourceInterval", 1800)
        self.errorsDampenFactor = args.get("errorsDampenFactor", 20)
        self.errorsCount = 0;
        self.mutex = threading.Lock()
        self.signal = threading.Event()
        self.items = []
        self.hostId = DataDispatcher.resolveHostId(args)
        self.agentId = DataDispatcher.resolveAgentId(args, self.hostId)
        self.serverLabel = DataDispatcher.resolveServerLabel(args, self.hostId, self.agentId)
        self.appName = DataDispatcher.resolveApplicationName(args.get("applicationName", None))
        self.lastHeartbeatTime = 0
        self.lastHeartbeatCount = 0
        self.lastSyncPropertiesTime = 0
        self.commandSender = commandSender

    @staticmethod
    def convertToTraceEssence(props):
        if (props is None) or (len(props) <= 0):
            return None
        
        flavor = props.get("flavor", "unknown")
        return { "essenceName": flavor, "essenceProperties": props }

    def createHeartbeatCommand(self, curTime):
        timeDiff = curTime - self.lastHeartbeatTime
        if timeDiff < self.flushInterval:
            return None

        cmd = { "AgentHeartbeatCommand": {                     \
                    "serverResource": {                         \
                        "ServerResource": {                     \
                            "key": {                            \
                                "name": self.agentId,           \
                                "type": "Server"                \
                            },                                  \
                            "label": self.serverLabel,          \
                            "serverName": {                     \
                               "name": self.agentId             \
                            }                                   \
                        }                                       \
                    },                                          \
                    "hostResource": {                           \
                        "ServerResource": {                     \
                            "key": {                            \
                                "name": self.hostId,            \
                                "type": "Server"                \
                            },                                  \
                            "label": self.hostId,               \
                                "serverName": {                 \
                                      "name": self.hostId       \
                                }                               \
                            }                                   \
                    },                                          \
                "config": {                                     \
                    "properties" : {                            \
                        "buildInfoTimestamp": "Unknown",        \
                        "buildInfoVersion": __version__,        \
                        "configVersion": 1,                     \
                        "heartbeatInterval": self.flushInterval * 1000,         \
                        "maxTracesSentPerMinute": 60 / self.flushInterval,      \
                        "syncPropsBeatInterval": self.syncResourceInterval * 1000 \
                    }                                           \
                },                                              \
                "beat": self.lastHeartbeatCount,                \
                "timeStampMS": int(curTime * 1000)              \
            }                                                   \
        }
        
        if self.logger.traceEnabled:
            self.logger.trace("Sending heartbeat - count=%d" % self.lastHeartbeatCount)

        self.lastHeartbeatTime = curTime
        self.lastHeartbeatCount += 1
        return cmd


    @staticmethod
    def sanitizePropertyValue(value):
        if value is None:
            return "None"
        elif isinstance(value, unicode):
            return DataDispatcher.sanitizePropertyValue(value.encode('utf-8'))
        elif isinstance(value, str):
            return value.replace('\\', '/')
        else:
            return value

    @staticmethod
    def createPropertiesEntries(prefix, props):
        entries = {}

        if (props is None) or (len(props) <= 0):
            entries[prefix] = { "val": 'empty', "important": False }
            return entries
        
        for key,value in props.items():
            propName= "%s.%s" % (prefix, key)
            propName = propName.replace(':', '.')   # some crazy Windows variables have these names
            propValue = DataDispatcher.sanitizePropertyValue(value)
            entries[propName] = { "val": propValue, "important": False }

        return entries

    def createResourcePropertiesCommand(self, curTime):
        timeDiff = curTime - self.lastSyncPropertiesTime
        if timeDiff < self.syncResourceInterval:
            return None

        cmd = { "SyncResourcePropertiesCommand": {             \
                    "agentName": {                              \
                            "name": self.agentId,               \
                    },                                          \
                    "agentHostId": {                            \
                            "name": self.hostId,                \
                    },                                          \
                    "resourceKey": {                            \
                        "name" : self.agentId,                  \
                        "type" : "Server"                       \
                    },                                          \
                    "resourceProperties" : {                    \
                        "resourceKey": {                        \
                                "name" : self.agentId,          \
                                "type" : "Server"               \
                            },                                  \
                        "properties" : DataDispatcher.createPropertiesEntries('sysenv', os.environ) \
                    }                                           \
            }                                                   \
        }

        if self.logger.traceEnabled:
            self.logger.trace("Sending sync. command")
        self.lastSyncPropertiesTime = curTime
        return cmd

    def wrapTraceEssences(self, appEssences):
        # TODO generate a trace ID
        return {                                                        \
            "TraceEssenceCommand": {                                    \
                "applicationName": {                                    \
                    "name": "localhost|%s" % self.appName               \
                },                                                      \
                "traceId": "python-03777347-7365-10281713-%s" % self.agentId,  \
                "traceEssence": appEssences                             \
            }                                                           \
        }

    def createCommandsList(self, essences):
        commands = []
        
        curTime = time.time()
        heartbeat = self.createHeartbeatCommand(curTime);
        if not heartbeat is None:
            commands.append(heartbeat)

        syncCmd = self.createResourcePropertiesCommand(curTime)
        if not syncCmd is None:
            commands.append(syncCmd)

        if (essences is None) or (len(essences) <= 0):
            return commands

        cmd = self.wrapTraceEssences(essences)
        commands.append(cmd)
        return commands

    def flushPendingItems(self):
        # see https://docs.python.org/2/library/threading.html#using-locks-conditions-and-semaphores-in-the-with-statement
        with self.mutex:
            pendingItems = self.items;
            self.items = []

        essences = None
        numPending = len(pendingItems)
        if numPending > 0:
            if self.logger.debugEnabled:
                self.logger.debug("Flushing %d items" % numPending)

            essences = []
            itemIndex = 1
            for item in pendingItems:
                try:
                    if self.logger.traceEnabled:
                        self.logger.trace("[%d/%d]: %s" % (itemIndex, numPending, item))
                    essence = DataDispatcher.convertToTraceEssence(item)
                    if essence is None:
                        continue
                    essences.append(essence)
                except Exception as err:
                    self.logger.warning("%s on convert item=%s: %s " % (err.__class__.__name__, item, str(err)), err)
                finally:
                    itemIndex += 1
        else:
            if self.logger.traceEnabled:
                self.logger.trace("No items to flush")
        
        commands = self.createCommandsList(essences)
        
        try:
            if self.commandSender.transmitCommands(commands):
                if self.errorsCount > 0:
                    if self.logger.debugEnabled:
                        self.logger.debug("Re-established connection with dashboard")
                    self.errorsCount = 0
        except Exception as err:
            if self.errorsCount <= 0: 
                self.logger.warning("Failed (%s) to send %d commands: %s " % (err.__class__.__name__, len(commands), str(err)), err)
            self.errorsCount += 1
            if self.errorsCount >= self.errorsDampenFactor:
                self.errorsCount = 0
        else:
            if self.logger.debugEnabled:
                self.logger.debug("Sent %d commands" % len(commands))
            if self.logger.traceEnabled:
                for cmd in commands:
                    self.logger.trace("Sent %s" % json.dumps(cmd, sort_keys=True))

    def generateCorrelationId(self, context='default'):
        return "python-%s-%s-3777347-%s-7365-%s-%s" % (self.agentId, self.appName, context, str((int) (time.time() * 1000000)), str(random.randint(1, 100000000)))

    def normalizeProperties(self, props):
        if not 'application' in props:
            props['application'] = self.appName
        if not 'agentid' in props:
            props['agentid'] = self.agentId
        if not 'agenthost' in props:
            props['agenthost'] = self.hostId
        if not 'origin' in props:
            props['origin'] = 'python-bci'
        if not 'correlation' in props:
            props['correlation'] = self.generateCorrelationId()
        return props

    def addItem(self, props):
        if (props is None) or (len(props) <= 0):
            return False

        props = self.normalizeProperties(props)

        # see https://docs.python.org/2/library/threading.html#using-locks-conditions-and-semaphores-in-the-with-statement
        with self.mutex:
            self.items.append(props)
            numPending = len(self.items)

        if self.logger.traceEnabled:
            self.logger.trace("addItem(pending=%d): %s" % (numPending, json.dumps(props, sort_keys=True)))

        if numPending >= self.maxItems:
            if self.logger.debugEnabled:
                self.logger.debug("Flushing %d items due to max. limit=%d" % (numPending, self.maxItems))
            self.signal.set()

        return True

    def run(self):
        self.logger.info("Waiting...")
        while True:
            if self.signal.wait(self.flushInterval):
                self.signal.clear()
                if self.logger.debugEnabled:
                    self.logger.debug("Awakened by signal")

            self.flushPendingItems()

# ----------------------------------------------------------------------------
