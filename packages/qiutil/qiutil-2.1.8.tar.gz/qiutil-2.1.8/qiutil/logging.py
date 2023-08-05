# Absolute import (the default in a future Python release) resolves
# the logging import as the Python standard logging module rather
# than this module of the same name.
from __future__ import absolute_import
import os
import logging
import logging.config
import yaml
from . import collections as qicollections


def logger(name):
    """
    This method is the preferred way to obtain a logger.

    Example:

    >>> from qiutil.logging import logger
    >>> logger(__name__).debug("Starting my application...")

    :param name: the caller's context ``__name__``
    :return: the Python Logger instance
    """
    # Configure on demand.
    if not hasattr(logger, 'configured'):
        configure(name)

    return logging.getLogger(name)


def configure(app, cfg_file=None, **opts):
    """
    Configures the global logger. The logging configuration is obtained from
    from the given keyword arguments and the YAML_ logging configuration files.
    The following logging configuration files are loaded in low-to-high
    precedence:

    - the ``qiutil`` module ``conf/logging.yaml`` file

    - the ``logging.yaml`` file in the current directory

    - the file specified by the ``LOG_CFG`` environment variable

    - the *cfg_file* parameter

    The ``opts`` keyword arguments specify simple logging parameters that
    override the configuration file settings. The keyword arguments
    can include the *filename* and *level* short-cuts, which are handled
    as follows:

    - if the *filename* is None, then file logging is disabled. Otherwise,
      the file handler file name is set to the *filename* value.

    - The *level* is set for the ``application`` logger. In addition, if
      the ``application`` logger has a file handler, then that file handler
      level is set. Otherwise, the console handler level is set.

    The logging configuration file ``formatters``, ``handlers`` and
    ``loggers`` sections are updated incrementally. For example, the
    ``conf/logging.yaml`` source distribution file defines the ``default``
    formatter ``format`` and ``datefmt``. If the  ``logging.yaml`` file in
    the current directory overrides the ``format`` but not the ``datefmt``,
    then the default ``datefmt`` is retained rather than unset. Thus, a custom
    logging configuration file need define only the settings which override
    the default configuration.

    By default, ``ERROR`` level messages are written to the  console.
    If the log file is set, then the default logger writes ``INFO`` level
    messages to a rotating log file.
    
    If the file handler is enabled, then this :meth:`qiutil.logging.configure`
    method ensures that the log file parent directory exists.

    Examples:

    - Write to the log:

      >>> from qiutil.logging import logger
      >>> logger(__name__).debug("Started the application...")

      or, in a class instance:

      >>> from qiutil.logging import logger
      >>> class MyApp(object):
      ...     def __init__(self):
      ...         self._logger = logger(__name__)
      ...     def start(self):
      ...         self._logger.debug("Started the application...")

    - Write debug messages to the file log:

      >>> import qiutil
      >>> qiutil.logging.configure(level='DEBUG')

    - Set the log file:

      >>> import qiutil
      >>> qiutil.logging.configure(filename='log/myapp.log')

    - Define your own logging configuration:

      >>> import qiutil
      >>> qiutil.logging.configure('/path/to/my/conf/logging.yaml')

    - Simplify the console log message format::

        ./logging.yaml:
        ---
        formatters:
          simple:
            format: '%(name)s - %(message)s'

        handlers:
          console:
            formatter: simple

    .. _YAML: http://www.yaml.org

    :param app: the application name
    :param cfg_file: the optional custom configuration YAML file
    :param opts: the Python ``logging.conf`` options, as well as the
        following short-cuts:
    :keyword filename: the log file path
    :keyword level: the file handler log level
    """
    # Load the configuration files.
    cfg = _load_config(app, cfg_file)

    # The options override the configuration files.
    if 'filename' in opts:
        fname = opts['filename']
        if fname:
            # Reset the log file.
            cfg['handlers']['file_handler']['filename'] = fname
        else:
            # Disable the file handler and retain only
            # the console handler.
            cfg['loggers'][app]['handlers'] = ['console']

    # The log level is set in both the logger and the handler,
    # and the more restrictive level applies. Therefore, set
    # the log level in both places.
    level = opts.pop('level', None)
    if level:
        cfg['loggers'][app]['level'] = level
        if 'file_handler' in cfg['loggers'][app]['handlers']:
            cfg['handlers']['file_handler']['level'] = level
        else:
            cfg['handlers']['console']['level'] = level

    # Add the other options, if any.
    qicollections.update(cfg, opts, recursive=True)

    # Ensure that the log file parent directory exists.
    if 'file_handler' in cfg['loggers'][app]['handlers']:
        log_file = cfg['handlers']['file_handler'].get('filename')
        if not log_file:
            raise ValueError("The logging configuration file handler is enabled"
                             " but the log file name is not set.")
        # Make the runtime path absolute for clarity.
        log_file = os.path.abspath(log_file)
        cfg['handlers']['file_handler']['filename'] = log_file
        # Make the log file parent directory, if necessary.
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

    # Configure the logger.
    logging.config.dictConfig(cfg)

    # Set the logger configured flag.
    setattr(logger, 'configured', True)


LOG_CFG_ENV_VAR = 'LOG_CONFIG'
"""The user-defined environment variable logging configuration file path."""

LOG_CFG_FILE = 'logging.yaml'
"""The optional current working directory logging configuration file name."""

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
"""The ``qiutil`` package directory."""

DEF_LOG_CFG = os.path.join(BASE_DIR, 'conf', LOG_CFG_FILE)
"""The default application logging configuration file path."""


def _load_config(app, cfg_file=None):
    """
    Loads the logger configuration files, as described in
    :meth:`qiutil.logging.configure`.

    :return: the logging configuration dictionary
    :raises ValueError: if the configuration file argument is specified
        but does not exist
    """
    # The base config file.
    config = _load_config_file(DEF_LOG_CFG)
    # Rename the application logger.
    loggers = config['loggers']
    loggers[app] = loggers.pop('application')
    
    # The custom configuration files.
    custom_cfg_files = _find_custom_config_files(cfg_file)
    # Load the custom configurations.
    custom_cfgs = (_load_config_file(f) for f in custom_cfg_files)
    # Update the base configuration.
    qicollections.update(config, *custom_cfgs, recursive=True)

    return config


def _find_custom_config_files(cfg_file):
    """
    Finds the custom logging configuration files, as described in
    :meth:`qiutil.logging.configure`.

    :param cfg_file: the custom configuration file argument
    :return: the custom configuration file list
    :raises ValueError: if the configuration file argument is specified
        but does not exist
    """
    # The config files list.
    config_files = []
    
    # The environment variable log configuration file.
    env_cfg_file = os.getenv(LOG_CFG_ENV_VAR, None)
    if env_cfg_file and os.path.exists(env_cfg_file):
        config_files.append(env_cfg_file)

    # The current directory log configuration file.
    if os.path.exists(LOG_CFG_FILE):
        config_files.append(LOG_CFG_FILE)

    # The argument log configuration file.
    if cfg_file:
        if os.path.exists(cfg_file):
            config_files.append(cfg_file)
        else:
            raise ValueError("Configuration file not found: %s" % cfg_file)

    return config_files


def _load_config_file(filename):
    """
    Loads the given logger configuration file.

    :param: filename: the log configuration file path
    :return: the parsed configuration parameter dictionary
    """
    with open(filename) as fs:
        return yaml.load(fs)
