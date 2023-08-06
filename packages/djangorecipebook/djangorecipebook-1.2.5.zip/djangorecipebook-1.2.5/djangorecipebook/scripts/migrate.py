"""
Calls the management script with the 'migrate' command
"""

from .manage import manage_main


def main(settings_module, *args):
    manage_main(settings_module, 'migrate', *args)
