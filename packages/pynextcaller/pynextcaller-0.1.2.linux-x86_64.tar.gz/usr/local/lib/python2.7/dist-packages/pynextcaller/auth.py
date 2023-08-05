from __future__ import unicode_literals
from base64 import b64encode


__all__ = (
    'BasicAuth',
)


class BasicAuth(object):
    """Basic auth class"""
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_headers(self):
        """Prepare auth_headers"""
        value = b64encode(
            ("{0}:{1}".format(self.username, self.password)).encode('utf-8')
        ).decode('utf-8')
        return {'Authorization': 'Basic {0}'.format(value)}

    def __call__(self):
        return self.get_headers()
