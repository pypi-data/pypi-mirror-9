# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
try:
    from unittest import mock
except ImportError:
    import mock
from ..client import NextCallerClient, NextCallerPlatformClient
from .. import transport


class BaseTestCase(unittest.TestCase):

    class FakeResponse(object):
        pass

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)
        self.client = None
        self.fake_response = None
        self.request_patcher = None

    def patch_http_request(self, result):
        self.mock.return_value = result

    def setUp(self):
        username = 'username'
        password = 'password'
        self.api_request = transport.api_request
        self.mock = mock.Mock()
        transport.api_request = self.mock
        self.client = NextCallerClient(username, password)
        self.fake_response = self.FakeResponse()
        self.fake_response.status_code = 204

    def tearDown(self):
        transport.api_request = self.api_request


class BasePlatformTestCase(BaseTestCase):

    def setUp(self):
        username = 'username'
        password = 'password'
        self.platform_username = 'test_username'
        self.api_request = transport.api_request
        self.mock = mock.Mock()
        transport.api_request = self.mock
        self.client = NextCallerPlatformClient(username, password)
        self.fake_response = self.FakeResponse()
        self.fake_response.status_code = 204
