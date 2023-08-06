"""
Creates the wsgi application
"""

# derived from R van Laar's djangorecipe

import os
import sys
import logging
from importlib import import_module


def setup_logging(logfile, level, logger_name):

    if logfile:
        # setup logging
        class StdStrLogger(object):
            def __init__(self, logger, level):
                self.logger = logger
                self.log_level = level

            def write(self, data):
                for line in data.rstrip().splitlines():
                    self.logger.log(self.log_level, line.rstrip())

        logger = logging.getLogger(logger_name)

        logger.setLevel(level)
        handler = logging.FileHandler(logfile)
        handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s:%(levelname)s:%(message)s',
            datefmt='%Y%m%d %H:%M:%S',)
        )
        logger.addHandler(handler)

        sys.stdout = StdStrLogger(logger, logging.INFO)
        sys.stderr = StdStrLogger(logger, logging.ERROR)


def main(settings_file, logfile=None, level=logging.INFO, application=None):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_file)

    setup_logging(logfile, level, 'wsgi_outerr_logger')

    if application is None:
        # using default application from django core
        from django.core.wsgi import get_wsgi_application
        wsgi_app = get_wsgi_application()
    else:
        # an application is provided as a path, import it
        module, app = application.rsplit('.', 1)
        wsgi_app = getattr(import_module(module), app)

    return wsgi_app
