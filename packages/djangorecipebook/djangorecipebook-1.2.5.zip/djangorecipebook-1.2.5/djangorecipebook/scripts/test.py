"""
Calls the management script with the 'test' command
"""

from .manage import manage_main


def main(settings_module, *args):
    manage_main(settings_module, 'test', *args)
