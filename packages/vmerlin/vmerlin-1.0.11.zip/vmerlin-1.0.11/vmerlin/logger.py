#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 VMware.
# All rights reserved.

import sys
import time
import traceback

# ----------------------------------------------------------------------------

class LogLevel(object):
    def __init__(self, name, value):
        self.levelName = name
        self.levelValue = value

    @property
    def name(self):
        return self.levelName

    @name.setter
    def name(self, value):
        raise NotImplementedError("Log level name is immutable")

    @property
    def value(self):
        return self.levelValue
    
    @value.setter
    def value(self, number):
        raise NotImplementedError("Log level value is immutable")

    def __str__(self):
        return "%s[%s]" % (self.name % str(self.value))

# ----------------------------------------------------------------------------

class Logger(object):
    # Because of some Python limitations we need to define these here 
    OFF=LogLevel('OFF', 10000)
    ERROR=LogLevel('ERROR', 1000)
    WARNING=LogLevel('WARNING', 900)
    INFO=LogLevel('INFO', 800)
    DEBUG=LogLevel('DEBUG', 700)
    TRACE=LogLevel('TRACE', 600)
    ALL=LogLevel('ALL', 0)
    LEVELS=[ OFF, ERROR, WARNING, INFO, DEBUG, TRACE, ALL ]

    def __init__(self, name):
        self.loggerName = name

    @property    
    def name(self):
        return self.loggerName

    @name.setter
    def name(self,value):
        raise NotImplementedError("Logger name is immutable")

    @property
    def errorEnabled(self):
        return self.levelEnabled(Logger.ERROR)

    @errorEnabled.setter
    def errorEnabled(self, value):
        raise NotImplementedError("Not allowed to modify ERROR enabled state for %s" % self.name)

    def error(self, msg, err=None):
        self.log(Logger.ERROR, msg, err)

    @property
    def warningEnabled(self):
        return self.levelEnabled(Logger.WARNING)

    @warningEnabled.setter
    def warningEnabled(self, value):
        raise NotImplementedError("Not allowed to modify WARNING enabled state for %s" % self.name)

    def warning(self, msg, err=None):
        self.log(Logger.WARNING, msg, err)

    @property
    def infoEnabled(self):
        return self.levelEnabled(Logger.INFO)

    @infoEnabled.setter
    def infoEnabled(self, value):
        raise NotImplementedError("Not allowed to modify INFO enabled state for %s" % self.name)

    def info(self, msg, err=None):
        self.log(Logger.INFO, msg, err)

    @property
    def debugEnabled(self):
        return self.levelEnabled(Logger.DEBUG)

    @debugEnabled.setter
    def debugEnabled(self, value):
        raise NotImplementedError("Not allowed to modify DEBUG enabled state for %s" % self.name)

    def debug(self, msg, err=None):
        self.log(Logger.DEBUG, msg, err)

    @property
    def traceEnabled(self):
        return self.levelEnabled(Logger.TRACE)

    @traceEnabled.setter
    def traceEnabled(self, value):
        raise NotImplementedError("Not allowed to modify TRACE enabled state for %s" % self.name)

    def trace(self, msg, err=None):
        self.log(Logger.TRACE, msg, err)

    def log(self, level, msg, err=None):
        if self.levelEnabled(level):
            self.appendLog(level, msg, err)
    
    def appendLog(self, level, msg, err=None):
        raise NotImplementedError("%s#appendLog(%s)[%s] not implemented" % (self.__class__.__name__, level.name, msg))

    def writeLogMessage(self, level, msg):
        raise NotImplementedError("%s#writeLogMessage(%s) not implemented" % (self.__class__.__name__, msg))
    
    def levelEnabled(self, level):
        raise NotImplementedError("%s#levelEnabled(%s) not implemented" % (self.__class__.__name__, level.name))

    def __str__(self):
        return self.name

    @staticmethod
    def fromLevelName(name):
        if (not name) or (len(name) <= 0):
            return None
        
        effectiveName = name.upper()
        for level in Logger.LEVELS:
            if level.name == effectiveName:
                return level
        
        return None

    @staticmethod
    def logHelp(logger, lines):
        if (not lines) or (len(lines) <= 0):
            return
        
        for line in lines:
            logger.info(line)

    @staticmethod
    def resolveThreshold(args, key="threshold", defaultLevel="INFO"):
        name = defaultLevel
        if not args is None:
            name = args.get(key, defaultLevel)
        return Logger.fromLevelName(name)

# ----------------------------------------------------------------------------
 
class StreamLogger(Logger):
    def __init__(self, name, args):
        super(StreamLogger, self).__init__(name)

        self.targetStream = None
        self.autoFlush = args.get("autoFlush", True)
        self.dateTimeFormat = args.get("format", "%Y-%m-%d %H:%M:%S.%f")
        self.maxStackTraceDepth = args.get("stackTraceDepth", 10)
        self.threshold = Logger.resolveThreshold(args)
        if self.threshold is None:
            self.threshold = LogLevel.OFF
    
    def levelEnabled(self, level):
        if self.targetStream is None:
            return False
        elif not level or not self.threshold:
            return False
        elif level.value >= self.threshold.value:
            return True
        else:
            return False

    def appendLog(self, level, msg, err=None):
        timestamp = time.strftime(self.dateTimeFormat)

        if msg:
            if '\n' in msg:
                for line in msg.splitlines(False):
                    self.writeLogMessage(level, "%s [%s] [%s] %s" % (timestamp, level.name, self.name, line))
            else:
                self.writeLogMessage(level, "%s [%s] [%s] %s" % (timestamp, level.name, self.name, msg))
        if err:
            self.writeLogMessage(level, "%s [%s] [%s] %s: %s" % (timestamp, level.name, self.name, err.__class__.__name__, str(err)))
            
            if self.maxStackTraceDepth > 0:
                # TODO this doesn't quite do the job - by the time it is here, most stack trace data is gone...
                traceValue = traceback.format_exc(self.maxStackTraceDepth)
                lines = traceValue.splitlines()
                for traceLine in lines:
                    self.writeLogMessage(level, "%s [%s] %s %s" % (timestamp, level.name, self.name, traceLine))

    def writeLogMessage(self, level, msg):
        self.targetStream.write("%s\n" % msg)
        if self.autoFlush:
            self.targetStream.flush()

# ----------------------------------------------------------------------------
        
class ConsoleLogger(StreamLogger):
    def __init__(self, name, args):
        super(ConsoleLogger, self).__init__(name, args)

        target = args.get("target", "stdout").lower()
        if target == "stderr":
            self.targetStream = sys.stderr
        else:
            self.targetStream = sys.stdout

# ----------------------------------------------------------------------------

class EmptyLogger(Logger):
    def __init__(self, name, args):
        super(EmptyLogger, self).__init__(name)

    def levelEnabled(self, level):
        return False

    def appendLog(self, level, msg, err=None):
        pass

# ----------------------------------------------------------------------------

class LoggingLogger(Logger):
    def __init__(self, name, args):
        super(LoggingLogger, self).__init__(name)
        import logging
        self.logger = logging.getLogger(name)

    @staticmethod
    def toLoggingLevel(level):
        levelName = None
        if isinstance(level, str):
            levelName = level
        elif not level is None:
            levelName = level.name
        if (levelName is None) or (len(levelName) <= 0):
            return None
        
        levelName = levelName.upper()
        import logging
        if levelName == Logger.ERROR.name:
            return logging.ERROR
        elif levelName == Logger.WARNING.name:
            return logging.WARNING
        elif levelName == Logger.INFO.name:
            return logging.INFO
        elif (levelName == Logger.DEBUG.name) or (levelName == Logger.TRACE.name):
            return logging.DEBUG
        elif levelName == Logger.ALL.name:
            return logging.NOTSET
        elif levelName == Logger.OFF.name:
            return None
        else:
            return None
        
    def levelEnabled(self, level):
        ll = LoggingLogger.toLoggingLevel(level)
        if ll is None:
            return False
        elif self.logger.isEnabledFor(ll):
            return True
        else:
            return False

    def appendLog(self, level, msg, err=None):
        ll = LoggingLogger.toLoggingLevel(level)
        if ll is None:
            return
        
        self.logger.log(ll, msg, exc_info=err)

# ----------------------------------------------------------------------------

class LogFactory(object):
    def __init__(self, args):
        self.implementation = args.get("implementation", "console")
        self.configuration = args.get(self.implementation, None)
    
    def getLogger(self, name):
        if self.implementation == 'console':
            return ConsoleLogger(name, self.configuration)
        elif self.implementation == 'logging':
            return LoggingLogger(name, self.configuration)
        else:
            return EmptyLogger(name, self.configuration)

# ----------------------------------------------------------------------------

class LoggingClass(object):
    def __init__(self, logFactory, args):
        self.logFactory = logFactory
        self.logger = logFactory.getLogger(self.__class__.__name__)
        self.args = args

# ----------------------------------------------------------------------------
