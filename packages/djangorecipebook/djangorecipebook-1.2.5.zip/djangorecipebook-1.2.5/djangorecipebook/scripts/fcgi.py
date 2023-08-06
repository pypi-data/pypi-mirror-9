"""
Runs FCGI handler
"""

import os
import logging

from .wsgi import setup_logging


def main(settings_file, logfile=None, level=logging.INFO):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_file)

    if logfile:
        setup_logging(logfile, level, 'fcgi_outerr_logger')

    # Run FCGI handler for the application
    from django.core.servers.fastcgi import runfastcgi
    runfastcgi(method="threaded", daemonize="false")
