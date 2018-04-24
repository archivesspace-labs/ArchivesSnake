import logging
import sys, os
import structlog
from copy import copy
import re

def copy_config(config):
    '''Copy relevant information from one config to another.'''

    new_config = {}
    new_logging = config['logging'].copy()
    new_structlog = {k:copy(v) for k,v in config['structlog'].items()}

    new_config.update(logging=new_logging, structlog=new_structlog)
    return new_config

# Regex to Match down or mixed-case usage of standard logging levels
canonical_levels = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET',)
level_re = re.compile(
    r"|".join((r'^{}$'.format(level) for level in canonical_levels)),
    re.I
)

already_configured = False
def setup_logging(config=None, level=None, stream=None):
    '''sets up both logging and structlog.'''
    global already_configured
    if not already_configured:
        from_env = os.environ.get('ASNAKE_LOG_CONFIG', None)
        default = configurations.get(from_env, DEFAULT_CONFIG)

        if not config:
            config = copy_config(DEFAULT_CONFIG)

        level = level or config.get('level', None) or logging.INFO
        if isinstance(level, str) and level_re.match(level):
            level = getattr(logging, level.upper())

        if stream:
            config['logging']['stream'] = stream

        logging.basicConfig(**config['logging'])
        l = logging.getLogger('asnake')
        l.setLevel(level)
        structlog.configure(**config['structlog'])
        already_configured = True
    else:
        raise RuntimeError("Attempted to configure logging when it has already been configured")

def get_logger(name=None):
    if not already_configured:
        setup_logging()
    return structlog.get_logger(name)

# Log format is standard across all provided defaults
# This amounts to a log of serialized JSON events with UTC timestamps and various
# useful information attached, which formats exceptions passed to logging methods in exc_info
def default_structlog_conf(**overrides):
    '''Generate a default configuration for structlog'''
    conf = {
        "logger_factory": structlog.stdlib.LoggerFactory(),
        "wrapper_class":structlog.stdlib.BoundLogger,
        "cache_logger_on_first_use": True,
        "processors": [
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.TimeStamper(fmt='iso', utc=True),
            structlog.processors.JSONRenderer()]
    }
    conf.update(**overrides)
    return conf

def default_logging_conf(**overrides):
    '''Generate a default stdlib logging configuration.'''
    conf = {"level": logging.INFO, "format": "%(message)s", "stream": sys.stderr}
    conf.update(**overrides)
    return conf

# Provided example configurations for structlog.
configurations = {}

configurations['INFO_TO_STDERR'] = {
    "logging": default_logging_conf(),
    "structlog": default_structlog_conf()
}

configurations['INFO_TO_STDOUT'] = {
    "logging": default_logging_conf(stream=sys.stdout),
    "structlog": default_structlog_conf()
}

configurations['DEBUG_TO_STDERR'] = {
    "logging": default_logging_conf(level=logging.DEBUG),
    "structlog": default_structlog_conf(),
    "level": "DEBUG"
}

configurations['DEBUG_TO_STDOUT'] = {
    "logging": default_logging_conf(level=logging.DEBUG, stream=sys.stdout),
    "structlog": default_structlog_conf(),
    "level": "DEBUG"
}

configurations['DEFAULT_CONFIG'] = configurations['INFO_TO_STDERR']

# Expose these as constants for user convenience
globals().update(**configurations)
