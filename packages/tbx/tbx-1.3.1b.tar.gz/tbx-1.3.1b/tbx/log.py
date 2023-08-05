# coding: utf-8
"""
(c) 2013 - Ronan Delacroix
Logging Utils
:author: Ronan Delacroix
"""
import sys
import os
import logging
import logging.handlers
from . import code


def configure_logging_to_screen(debug=False):
    level = 'INFO'
    if debug:
        level = 'DEBUG'
    (script_folder, app_name) = code.get_app_name()
    settings = {'LOGGING_LEVEL': level, 'LOGGING_METHODS': ['SCREEN'], 'SCREEN_FORMAT': '%(message)s'}
    configure_logger(logging.getLogger(), app_name, settings=settings)


def configure_logging(log_name, settings={}, application_name=None):
    configure_logger(logging.getLogger(), log_name, settings=settings, application_name=application_name)


def configure_logger(logger, log_name, settings={}, application_name=None):

    log_level = settings.get('LOGGING_LEVEL', 'DEBUG')
    log_methods = settings.get('LOGGING_METHODS', ['SCREEN', 'FILE', 'SYSLOG'])

    logger.setLevel(log_level)
    
    if not hasattr(logger, 'handlers_added'):
        #we first remove all handlers  
        for handler in logger.handlers:
            logger.removeHandler(handler)

        #make handlers, that write the logs to screen, file, syslog
        if 'SCREEN' in log_methods:
            add_screen_logging(logger)

        if 'SYSLOG' in log_methods:# and ('SysLogHandler' in dir(logging)):
            add_syslog_logging(logger, settings)

        if 'FILE' in log_methods:
            add_file_logging(logger, log_name, application_name, settings)

        logger.propagate = True
    
        logger.handlers_added = True


def add_screen_logging(logger, settings={}):
    screen_format = settings.get('SCREEN_FORMAT', '%(levelname)s | %(message)s')
    write_to_screen_handler = logging.StreamHandler()
    screen_formatter = logging.Formatter(screen_format, '%Y-%m-%dT%H:%M:%S')
    write_to_screen_handler.setFormatter(screen_formatter)
    logger.addHandler(write_to_screen_handler)


def add_syslog_logging(logger, settings={}):
    #guessing syslog address
    syslog_address = settings.get('LOGGING_SYSLOG_ADDRESS', None)
    if not syslog_address:
        if sys.platform == 'darwin':
            syslog_address = '/var/run/syslog'
        else:
            syslog_address = '/dev/log'
    syslog_format = settings.get('SYSLOG_FORMAT', '[%(asctime)s] [%(filename)s:%(funcName)s:%(lineno)d]\t%(levelname)s - %(message)s')
    write_to_syslog_handler = logging.handlers.SysLogHandler(address=syslog_address)
    syslog_formatter = logging.Formatter(syslog_format, '%Y-%m-%dT%H:%M:%S')
    write_to_syslog_handler.setFormatter(syslog_formatter)
    logger.addHandler(write_to_syslog_handler)


def add_file_logging(logger, log_name, application_name, settings={}):
    (script_folder, app_name) = code.get_app_name()
    if not application_name:
        application_name = app_name

    log_folder = settings.get('LOGGING_FOLDER', None)
    if not log_folder:
        log_folder = os.path.join(script_folder, 'log')

    log_folder = log_folder.replace('<app_name>', application_name).replace('<name>', log_name)
    log_folder = os.path.abspath(log_folder)

    if not os.path.isdir(log_folder):
        try:
            os.makedirs(log_folder)
        except:
            print("Warning : permission denied to log in folder '%s'. Will attempt to log in '%s'" %
                  (log_folder, os.path.join(script_folder, 'log')))
            log_folder = os.path.join(script_folder, 'log')

    if not os.path.isdir(log_folder):
        try:
            os.makedirs(log_folder)
        except:
            print("Impossible to log with FILE handler to %s either, abandoning file logging." % log_folder)
            return

    if not os.access(log_folder, os.W_OK):
        print("Warning : permission denied to log in folder '%s'. Will attempt to log in '%s'" %
              (log_folder, os.path.join(script_folder, 'log')))
        log_folder = os.path.join(script_folder, 'log')
        try:
            os.makedirs(log_folder)
        except:
            print("Impossible to log with FILE handler to %s either, abandoning file logging." % log_folder)
            return

    file_format = settings.get('FILE_FORMAT', '[%(asctime)s] [%(filename)s:%(funcName)s:%(lineno)d]\t%(levelname)s - %(message)s')
    log_file = os.path.join(log_folder, log_name + ".txt")
    write_to_file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10000000, backupCount=10)
    file_formatter = logging.Formatter(file_format, '%Y-%m-%dT%H:%M:%S')
    write_to_file_handler.setFormatter(file_formatter)
    logger.addHandler(write_to_file_handler)