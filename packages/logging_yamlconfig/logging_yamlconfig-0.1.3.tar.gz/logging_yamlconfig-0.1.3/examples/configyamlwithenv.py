#!/bin/env python2

"""
A sample of YAML-based logging configuration.

The python standard logging library gets configured from YAML text.  In this sample configuration three loggers are
configured and each has a different level configured in a different way.
- The root logger is configured.
- The logger 'envlog' is configured using the environment variable LOGLEVEL.  This is to illustrate how you can use
the _ENV directive to customize configurations.
- The logger 'envdefaultlog' would be configured using a variable, but since it doesnt exist the default in the _ENV
directive is used.  This is to illustrate the alternate syntax of the _ENV directive for default values.
"""

import os
import logging
from StringIO import StringIO

from logging_yamlconfig import logging_yaml_init_fh

# make a logging configuration
configtxt = """
version: 1
handlers:
  console:
    class: logging.StreamHandler
    stream: 'ext://sys.stdout'
loggers:
  envlog:
    level: _ENV:LOGLEVEL
  envdefaultlog:
    level: _ENV:NONEXISTENTENVVAR:CRITICAL
root:
  level: WARN
  handlers:
  - console
"""

yamlfile = StringIO(configtxt)

# demonstrate env var support in yaml- DEBUG loglevel
os.environ['LOGLEVEL'] = 'DEBUG'

# load the configuration with yaml dictconfig helper
logging_yaml_init_fh(yamlfile)

# create a logger
rootlog = logging.getLogger()           # the effective log level will be WARN, as specified in the config
envlog = logging.getLogger('envlog')    # the level will be DEBUG since we put that in the environment
envdefaultlog = logging.getLogger('envdefaultlog') # the environment variable (likely) doesn't exist so the default is used

# sample log messages- the different loggers will have different effective levels as determined by the yaml and the env
for log in rootlog, envlog, envdefaultlog:
    print '### logger:', log.name
    log.debug('debug message')
    log.info('info message')
    log.warn('warn message')
    log.error('error message')
    log.critical('critical message')

# vim: set ts=4 sw=4 expandtab:
