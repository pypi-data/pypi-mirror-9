import os
import re
import sys
import yaml
import logging.config


class YamlEnvLoader(yaml.Loader):
    """
    an extended YAML loader which can get values from environment variables where _ENV is specified, e.g.

    path: _ENV:PATH

    will be replaced with the PATH environment variable, such that the resulting dictionary will be equivalent to:

    { "path": os.environ['PATH'] }

    if the environment variable specified does not exist, the value will be None. you can otherwise specify a default
    value with the form:

    _ENV:VARNAME:DEFAULT

    NOTE: these _ENV statements will be replaced with either None, a string, an int, or a float depending solely on the
    content.  this interpretation was added because,even though environment variables are always strings, you might want
    to pass arguments to a handler for configuration which expects a number (maxBytes on RotatingFileHandler, or port on
    SocketHandler for example).
    """
    YAML_ENV_PATTERN = re.compile(r'^_ENV:(?P<envname>[^:]+)(:(?P<default>[^:]+))?$')

    def __init__(self, stream):
        yaml.add_implicit_resolver('!pathex', self.YAML_ENV_PATTERN, Loader=self)
        yaml.add_constructor('!pathex', self._pathex_constructor, Loader=self)
        super(YamlEnvLoader, self).__init__(stream)

    def _pathex_constructor(self, loader, node):
        value = self.construct_scalar(node)
        m = self.YAML_ENV_PATTERN.match(value)
        if m is None:
            return value
        else:
            envval = os.environ.get(m.group('envname'), m.group('default'))
            try:
                if int(envval) == float(envval):
                    envval = int(envval)
                else:
                    envval = float(envval)
            except (TypeError, ValueError):
                pass
            return envval


class ConfigLocator(object):
    """
    initialized with a search path and will return the first existent file on that path from the locate method.  this is
    the interface expected by the locator member of the configloader objects below.
    """
    DEFAULT_SEARCH_PATH = ['./pylogging.yaml',
                           '/etc/pylogging.yaml']

    def __init__(self, search_path=None, yaml_loader_class=yaml.BaseLoader):
        if search_path is None:
            search_path = self.DEFAULT_SEARCH_PATH

        self.search_path = search_path

    def locate(self):
        log_configs = filter(
            os.path.exists, map(os.path.abspath, self.search_path)
        )

        if len(log_configs) > 0:
            return log_configs[0]
        else:
            print >>sys.stderr, 'ERROR: could not find log configuration file in search path [%s]' % \
                                ', '.join(log_configs)
            sys.exit(1)


class LoggingYAMLConfigLoader(object):
    """
    yaml configuration helper for the standard python logger.  see the convenience methods named logging_yaml_init* for
    usage
    """
    def __init__(self, locator=None, yaml_loader_class=yaml.BaseLoader):
        if locator is None:
            locator = ConfigLocator()

        self.locator = locator
        self.yaml_loader_class = yaml_loader_class

    def configure(self):
        configpath = self.locator.locate()

        try:
            with open(configpath, 'r') as logfh:
                self.configure_fh(logfh)
        except Exception, e:
            print >>sys.stderr, "ERROR: could not open log file at \'%s\': %s" % (configpath, str(e),)
            sys.exit(1)

    def configure_fh(self, fh):
        try:
            logconfig = yaml.load(fh, Loader=self.yaml_loader_class)
        except Exception, e:
            print >>sys.stderr, "ERROR: could not deserialize logging yaml: %s" % str(e)
            sys.exit(1)

        self.configure_dict(logconfig)

    def configure_dict(self, dct):
        try:
            logging.config.dictConfig(dct)
        except Exception, e:
            print >>sys.stderr, "ERROR: could not configure logger with logging yaml- %s" % str(e)


class EnvLoggingYAMLConfigLoader(LoggingYAMLConfigLoader):
    def __init__(self, locator=None):
        super(EnvLoggingYAMLConfigLoader, self).__init__(locator, YamlEnvLoader)


def logging_yaml_init(search_path=None, env_in_yaml=True):
    """
    configures the logger using YAML from a search path, see
    https://docs.python.org/2/howto/logging.html#logging-advanced-tutorial for dictConfig format

    if the first file found along the path does not contain a valid logging configuration in YAML the process will exit
    (fail closed).

    :param search_path: optional, specifies a list of file paths to check for a yaml configuration file
    :param env_in_yaml: whether or not to extend the yaml loader with support for values of the form
    _ENV:<NAME>:<DEFAULT>
    :return: None
    """
    # make config locator
    if search_path is not None:
        locator = ConfigLocator(search_path)
    else:
        locator = ConfigLocator()

    # make loader
    if env_in_yaml:
        loader_class = EnvLoggingYAMLConfigLoader
    else:
        loader_class = LoggingYAMLConfigLoader

    loader = loader_class(locator)

    loader.configure()


def logging_yaml_init_fh(fh, env_in_yaml=True):
    """
    configures the logger using YAML from a filehandle, see
    https://docs.python.org/2/howto/logging.html#logging-advanced-tutorial for dictConfig format

    if the file handle does not contain a valid logging configuration in YAML the process will call sys.exit (fail
    closed).

    :param fh: an open filehandle containing yaml
    :param env_in_yaml: whether or not to extend the yaml loader with support for values of the form
    _ENV:<NAME>:<DEFAULT>
    :return: None
    """
    if env_in_yaml:
        loader_class = EnvLoggingYAMLConfigLoader
    else:
        loader_class = LoggingYAMLConfigLoader

    loader = loader_class()

    loader.configure_fh(fh)


def logging_yaml_init_dict(dct):
    """
    configures the python standard logger using a dictionary, see
    https://docs.python.org/2/howto/logging.html#logging-advanced-tutorial for dictConfig format

    if dictionary does not contain a valid logging configuration the process will call sys.exit (fail closed).

    :param dct: dictionary containing logger configuration
    :return:
    """
    loader = LoggingYAMLConfigLoader()

    loader.configure_dict(dct)


# vim: set ts=4 sw=4 expandtab:
