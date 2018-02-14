import logging
import sys
logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)

import structlog
'''Useful default values for structlog.

This amounts to a log of serialized JSON events with UTC timestamps and various useful information attached, which formats exceptions passed to logging methods in exc_info'''
if not structlog.is_configured():
    structlog.configure(logger_factory=structlog.stdlib.LoggerFactory(),
                        wrapper_class=structlog.stdlib.BoundLogger,
                        cache_logger_on_first_use=True,
                        processors=[
                            structlog.stdlib.add_logger_name,
                            structlog.stdlib.add_log_level,
                            structlog.stdlib.PositionalArgumentsFormatter(),
                            structlog.processors.StackInfoRenderer(),
                            structlog.processors.format_exc_info,
                            structlog.processors.UnicodeDecoder(),
                            structlog.processors.TimeStamper(fmt='iso', utc=True),
                            structlog.processors.JSONRenderer()])

from .web_client import ASnakeClient
from .configurator import ASnakeConfig
