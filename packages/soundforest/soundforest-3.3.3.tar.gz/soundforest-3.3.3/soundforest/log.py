# coding=utf-8
"""Logging functions

Soundforest debug and file logging facilities

"""
import os
import sys
import fnmatch
import re
import urllib
import bz2
import gzip
import logging
import logging.handlers

from datetime import datetime, timedelta

from soundforest import SoundforestError

DEFAULT_LOGFORMAT = '%(module)s %(levelname)s %(message)s'
DEFAULT_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOGFILEFORMAT = '%(asctime)s %(module)s.%(funcName)s %(message)s'
DEFAULT_LOGSIZE_LIMIT = 2**20
DEFAULT_LOG_BACKUPS = 10

DEFAULT_SYSLOG_FORMAT = '%(message)s'
DEFAULT_SYSLOG_LEVEL =  logging.handlers.SysLogHandler.LOG_WARNING
DEFAULT_SYSLOG_FACILITY = logging.handlers.SysLogHandler.LOG_USER

# Mapping to set syslog handler levels via same classes as normal handlers
LOGGING_LEVEL_NAMES = ( 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
SYSLOG_LEVEL_MAP = {
    logging.handlers.SysLogHandler.LOG_DEBUG:   logging.DEBUG,
    logging.handlers.SysLogHandler.LOG_NOTICE:  logging.INFO,
    logging.handlers.SysLogHandler.LOG_INFO:    logging.INFO,
    logging.handlers.SysLogHandler.LOG_WARNING: logging.WARN,
    logging.handlers.SysLogHandler.LOG_ERR:     logging.ERROR,
    logging.handlers.SysLogHandler.LOG_CRIT:    logging.CRITICAL,
}

# Local syslog device varies by platform
if sys.platform == 'linux2' or fnmatch.fnmatch(sys.platform, '*bsd*'):
    DEFAULT_SYSLOG_ADDRESS = '/dev/log'
elif sys.platform == 'darwin':
    DEFAULT_SYSLOG_ADDRESS = '/var/run/syslog'
else:
    DEFAULT_SYSLOG_ADDRESS = ( 'localhost', 514 )

class SoundforestLogger(object):
    """SoundforestLogger

    Class for common script logging tasks. Implemented as singleton to prevent
    errors in duplicate handler initialization.

    """
    __instances = {}
    def __init__(self, name=None):
        name = name is not None and name or self.__class__.__name__

        if not SoundforestLogger.__instances.has_key(name):
            SoundforestLogger.__instances[name] = SoundforestLogger.LoggerInstance(name)

        self.__dict__['_SoundforestLogger__instances'] = SoundforestLogger.__instances
        self.__dict__['name'] = name

    class LoggerInstance(dict):
        """LoggerInstance

        Singleton implementation of logging configuration for one program

        """
        def __init__(self, name):
            self.name = name
            self.loglevel = logging.Logger.root.level
            self.register_stream_handler('default_stream')

        def __getattr__(self, attr):
            if attr in self.keys():
                return self[attr]
            raise AttributeError('No such LoggerInstance attribute: %s' % attr)

        def __get_or_create_logger__(self, name):
            if name not in self.keys():
                for logging_manager in logging.Logger.manager.loggerDict.values():
                    if hasattr(logging_manager, 'name') and logging_manager.name==name:
                        self[name] = logging.getLogger(name)
                        break

            if name not in self.keys():
                self[name] = logging.getLogger(name)

            return self[name]

        def __match_handlers__(self, handler_list, handler):
            def match_handler(a, b):
                if type(a) != type(b):
                    return False

                if isinstance(a, logging.StreamHandler):
                    for k in ('stream', 'name',):
                        if getattr(a, k) != getattr(b, k):
                            return False
                    return True

                if isinstance(a, logging.handlers.SysLogHandler):
                    for k in ( 'address', 'facility', ):
                        if getattr(a, k) != getattr(b, k):
                            return False
                    return True

                if isinstance(a, logging.handlers.HTTPHandler):
                    for k in ( 'host', 'url', 'method', ):
                        if getattr(a, k) != getattr(b, k):
                            return False
                    return True

                return True

            if not isinstance(handler, logging.Handler):
                raise LoggerError('Not an instance of logging.Handler: %s' % handler)

            if not isinstance(handler_list, list):
                raise LoggerError('BUG handler_list must be a list instance')

            for match in handler_list:
                if match_handler(match, handler):
                    return True

            return False

        def register_stream_handler(self, name, logformat=None, timeformat=None):
            """
            Register a common log stream handler
            """

            if logformat is None:
                logformat = DEFAULT_LOGFORMAT
            if timeformat is None:
                timeformat = DEFAULT_TIME_FORMAT

            logger = self.__get_or_create_logger__(name)
            handler = logging.StreamHandler()
            if self.__match_handlers__(self.default_stream.handlers, handler):
                return

            if not self.__match_handlers__(logger.handlers, handler):
                handler.setFormatter(logging.Formatter(logformat, timeformat))
                logger.addHandler(handler)

        def register_syslog_handler(self, name,
                address=DEFAULT_SYSLOG_ADDRESS,
                facility=DEFAULT_SYSLOG_FACILITY,
                default_level=DEFAULT_SYSLOG_LEVEL,
                socktype=None,
                logformat=None,
            ):

            if logformat is None:
                logformat = DEFAULT_SYSLOG_FORMAT

            if default_level not in SYSLOG_LEVEL_MAP.keys():
                raise LoggerError('Unsupported syslog level value')

            logger = self.__get_or_create_logger__(name)
            handler = logging.handlers.SysLogHandler(address, facility, socktype)
            handler.level = default_level
            if not self.__match_handlers__(logger.handlers, handler):
                handler.setFormatter(logging.Formatter(logformat))
                logger.addHandler(handler)
                logger.setLevel(self.loglevel)

        def register_http_handler(self, name, url, method='POST'):
            logger = self.__get_or_create_logger__(name)
            try:
                host, path = urllib.splithost(url[url.index(':')+1:])
            except IndexError, emsg:
                raise LoggerError('Error parsing URL %s: %s' % (url, emsg))

            handler = logging.handlers.HTTPHandler(host, url, method)
            if not self.__match_handlers__(logger.handlers, handler):
                logger.addHandler(handler)
                logger.setLevel(self.loglevel)

        def register_file_handler(self, name, directory,
                         logformat=None,
                         timeformat=None,
                         maxBytes=DEFAULT_LOGSIZE_LIMIT,
                         backupCount=DEFAULT_LOG_BACKUPS):
            """
            Register a common log file handler for rotating file based logs
            """

            if logformat is None:
                logformat = DEFAULT_LOGFILEFORMAT
            if timeformat is None:
                timeformat = DEFAULT_TIME_FORMAT

            if not os.path.isdir(directory):
                try:
                    os.makedirs(directory)
                except OSError:
                    raise LoggerError('Error creating directory: %s' % directory)
            logfile = os.path.join(directory, '%s.log' % name)

            logger = self.__get_or_create_logger__(name)
            handler = logging.handlers.RotatingFileHandler(
                filename=logfile,
                mode='a+',
                maxBytes=maxBytes,
                backupCount=backupCount
            )
            if not self.__match_handlers__(logger.handlers, handler):
                handler.setFormatter(logging.Formatter(logformat, timeformat))
                logger.addHandler(handler)
                logger.setLevel(self.loglevel)


        @property
        def level(self):
            return self._level
        @level.setter
        def level(self, value):
            if not isinstance(value, int):
                if value in LOGGING_LEVEL_NAMES:
                    value = getattr(logging, value)
                try:
                    value = int(value)
                    if value not in SYSLOG_LEVEL_MAP.values():
                        raise ValueError
                except ValueError:
                    raise ValueError('Invalid logging level value: %s' % value)

            for logger in self.values():
                if hasattr(logger, 'setLevel'):
                    logger.setLevel(value)
            self._level = value

        # Compatibility for old API
        @property
        def loglevel(self):
            return self.level
        @loglevel.setter
        def loglevel(self, value):
            self.level = value

        # compatibility for old API
        def set_level(self, value):
            self.level = value

    def __getattr__(self, attr):
        return getattr(self.__instances[self.name], attr)

    def __setattr__(self, attr, value):
        setattr(self.__instances[self.name], attr, value)

    def __getitem__(self, item):
        return self.__instances[self.name][item]

    def __setitem__(self, item, value):
        self.__instances[self.name][item] = value
