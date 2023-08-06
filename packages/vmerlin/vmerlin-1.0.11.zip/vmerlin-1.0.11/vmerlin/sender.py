#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import json
import requests

from .logger import LoggingClass
from .version import __version__

# ----------------------------------------------------------------------------

class CommandSender(LoggingClass):
    def __init__(self, logFactory, args):
        super(CommandSender, self).__init__(logFactory, args)
        self.jsonPrettyPrintIndent = args.get("jsonPrettyPrintIndent", None)
        if self.jsonPrettyPrintIndent <= 0:
            self.jsonPrettyPrintIndent = None

    def stringify(self, data):
        return json.dumps(data, indent=self.jsonPrettyPrintIndent, sort_keys=True)

    def transmitCommands(self, commands):
        if (commands is None) or (len(commands) <= 0):
            return False
        raise NotImplementedError("Should have implemented %s#transmitCommands()" % self.__class__.__name__)

# ----------------------------------------------------------------------------

"""
Used only for debugging
"""
class ConsoleCommandSender(CommandSender):
    def __init__(self, logFactory, args):
        super(ConsoleCommandSender, self).__init__(logFactory, args)

    def transmitCommands(self, commands):
        if (commands is None) or (len(commands) <= 0):
            return False

        for cmd in commands:
            self.logger.info(self.stringify(cmd))

# ----------------------------------------------------------------------------

class HttpCommandSender(CommandSender):
    @staticmethod
    def resolveProtocolPort(protocol):
        protocol = protocol.lower()
        if protocol == 'http':
            return 80
        elif protocol == 'https':
            return 443
        else:
            raise ValueError("Unknown protocol: %s" % protocol)

    def __init__(self, logFactory, args):
        super(HttpCommandSender,self).__init__(logFactory, args)
        self.protocol = args.get("protocol", "https")
        self.verifyCertificates = args.get("validateCertificates", True)
        self.host = args.get("host", "vmerlin.cf")
        self.port = args.get("port", (-1))
        if self.port <= 0:
            self.port = HttpCommandSender.resolveProtocolPort(self.protocol)
        self.contextPath = args.get("context", "insight/agent")
        self.url = "%s://%s:%s/%s" % (self.protocol, self.host, self.port, self.contextPath)
        self.responseTimeout = args.get("responseTimeout", 30)

        username = str(args.get("username", ""))    # in case username is all digits
        password = str(args.get("password", ""))    # in case password is all digits
        self.authData = None
        if (len(username) <= 0) or (len(password) <= 0):
            self.logger.warning("Non-authenticated access requested to %s" % self.url)
        else:
            self.authData = (username, password)
    
    def transmitCommands(self, commands):
        if (not commands) or (len(commands) <= 0):
            return False

        payload = self.stringify(commands)
        headers = {                                                     \
                   'User-Agent': "Python BCI/%s" % __version__,         \
                   'Content-Type': 'application/json; charset=utf-8',   \
                   'Content-Length': str(len(payload))                  \
                }
        r = requests.post(self.url, data=payload,           \
                          timeout=self.responseTimeout,     \
                          allow_redirects=False,            \
                          verify=self.verifyCertificates,   \
                          headers=headers,                  \
                          auth=self.authData)
        statusCode = r.status_code

        if self.logger.traceEnabled:
            for name,value in r.headers.items():
                self.logger.trace("    %s: %s" % (name, value))

        if statusCode == requests.codes.ok:
            if self.logger.debugEnabled:
                self.logger.debug("Posted %d commands to %s" % (len(commands), self.url))
            # TODO parse the response text and handle the commands
            return True
        else:
            raise IOError(statusCode, "Failed to send %d commands to %s" % (len(commands), self.url))

# ----------------------------------------------------------------------------
