from __future__ import unicode_literals
import unittest
try:
    from unittest import mock
except ImportError:
    import mock
try:
    from .base import BaseTestCase, BasePlatformTestCase
except (ValueError, ImportError):
    from pynextcaller.tests.base import BaseTestCase, BasePlatformTestCase


FRAUD_JSON_RESULT_EXAMPLE = '''
{
    "spoofed": "unknown",
    "fraud_risk": "medium"
}
'''


class FraudTestCase(BaseTestCase):

    def test_client_fraud(self):
        phone = '2125558383'
        self.patch_http_request(FRAUD_JSON_RESULT_EXAMPLE)
        res = self.client.get_fraud_level(phone)
        self.assertEqual(res['spoofed'], 'unknown')


class FraudPlatformTestCase(BasePlatformTestCase):

    def test_client_fraud(self):
        phone = '2125558383'
        platform_user = 'test_username'
        self.patch_http_request(FRAUD_JSON_RESULT_EXAMPLE)
        res = self.client.get_fraud_level(phone, platform_user)
        self.assertEqual(res['spoofed'], 'unknown')


if __name__ == '__main__':
    unittest.main()
