"""Handle logger File generation"""
import logging
import logging.config
from os import path
import os
from asynch.async_handler import AsyncExecutors
from pid.charger.load_properties import PrepareProperties
charged_properties = PrepareProperties()


application_path = os.path.dirname(__file__)
LOG_FILE_PATH = path.join(application_path, 'logging.config')
logging.config.fileConfig(LOG_FILE_PATH, disable_existing_loggers=True)

class Logger:
    """logging wrapper class
    To log in a particular module, import Logger class in that module and call
    LOGGER = Logger(__name__)
        LOGGER.info("msg")
            result -> [2020-05-07 16:20:44,438][TID-12684][INFO][logger_helper.py:21]-log message"""

    def __init__(self, name="default"):
        self.logger = logging.getLogger(name)
        charged_properties = PrepareProperties()
        self.async_mode = charged_properties.system_config["asynch"]["logger_async_mode"].lower()

    def info(self, msg, *args):
        """Asynchronous implementation of logging.info
        Log 'msg % args' with severity 'INFO'.
        To pass exception information, use the keyword argument exc_info with a true value, e.g.
        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)"""
        if self.async_mode == 'n':
            self.logger.info(msg, *args)
        else :
            executor = AsyncExecutors().get_logger_executor()
            executor.submit(self.logger.info, msg, *args)

    def debug(self, msg, *args):
        """Asynchronous implementation of logging.debug
        Log 'msg % args' with severity 'DEBUG'.
        To pass exception information, use the keyword argument exc_info with a true value, e.g.
        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)"""
        if self.async_mode == 'n':
            self.logger.debug(msg, *args)
        else :
            executor = AsyncExecutors().get_logger_executor()
            executor.submit(self.logger.debug, msg, *args)

    def error(self, msg, *args):
        """Asynchronous implementation of logging.error
        Log 'msg % args' with severity 'ERROR'.
        To pass exception information, use the keyword argument exc_info with a true value, e.g.
        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)"""
        if self.async_mode == 'n':
            self.logger.error(msg, *args)
        else :
            executor = AsyncExecutors().get_logger_executor()
            executor.submit(self.logger.error, msg, *args)

    def fatal(self, msg, *args):
        """Asynchronous implementation of logging.fatal
        Log 'msg % args' with severity 'FATAL'.
        To pass exception information, use the keyword argument exc_info with a true value, e.g.
        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)"""
        if self.async_mode == 'n':
            self.logger.fatal(msg, *args)
        else :
            executor = AsyncExecutors().get_logger_executor()
            executor.submit(self.logger.fatal, msg, *args)

    def critical(self, msg, *args):
        """Asynchronous implementation of logging.critical
        Log 'msg % args' with severity 'CRITICAL'.
        To pass exception information, use the keyword argument exc_info with a true value, e.g.
        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)"""
        if self.async_mode == 'n':
            self.logger.critical(msg, *args)
        else :
            executor = AsyncExecutors().get_logger_executor()
            executor.submit(self.logger.critical, msg, *args)

    def warning(self, msg, *args):
        """Asynchronous implementation of logging.warning
        Log 'msg % args' with severity 'WARNING'.
        To pass exception information, use the keyword argument exc_info with a true value, e.g.
        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)"""
        if self.async_mode == 'n':
            self.logger.warning(msg, *args)
        else :
            executor = AsyncExecutors().get_logger_executor()
            executor.submit(self.logger.warning, msg, *args)

    def exception(self, msg, *args):
        """Asynchronous implementation of logging.exception
        Log 'msg % args' with severity 'EXCEPTION'.
        To pass exception information, use the keyword argument exc_info with a true value, e.g.
        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)"""
        if self.async_mode == 'n':
            self.logger.exception(msg, *args)
        else :
            executor = AsyncExecutors().get_logger_executor()
            executor.submit(self.logger.exception, msg, *args)
    def log(self, level, msg, *args):
        """Asynchronous implementation of logging.log
        Log 'msg % args' with the integer severity 'level'.
        To pass exception information, use the keyword argument exc_info with a true value, e.g.
        logger.log(level, "We have a %s", "mysterious problem", exc_info=1)"""
        if self.async_mode == 'n':
            self.logger.log(msg, *args)
        else :
            executor = AsyncExecutors().get_logger_executor()
            executor.submit(self.logger.log, level, msg, *args)
