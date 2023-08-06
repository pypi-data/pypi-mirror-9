"""
Custom exception classes to avoid relying on third party packages
(like ... django!!)
"""


class ImproperlyConfigured(Exception):
    pass
