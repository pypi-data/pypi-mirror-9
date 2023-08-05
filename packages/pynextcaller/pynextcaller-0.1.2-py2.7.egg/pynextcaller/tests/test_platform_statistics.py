from __future__ import unicode_literals
import json
import unittest
try:
    from unittest import mock
except ImportError:
    import mock
try:
    from .base import BasePlatformTestCase
    from .test_by_phone import PHONE_JSON_RESULT_EXAMPLE
except (ValueError, ImportError):
    from pynextcaller.tests.base import BasePlatformTestCase
    from pynextcaller.tests.test_by_phone import PHONE_JSON_RESULT_EXAMPLE


PLATFORM_STATISTICS_JSON_RESULT_EXAMPLE = '''
{
    "object_list": [
        {
            "username": "test",
            "first_name": "",
            "last_name": "",
            "company_name": "",
            "email": "",
            "number_of_operations": 3,
            "successful_calls": {
                "201411": 3
            },
            "total_calls": {
                "201411": 3
            },
            "created_time": "2014-11-13 06:07:19.836404",
            "resource_uri": "/v2/platform_users/test/"
        }
    ],
   "page": 1,
    "has_next": false,
    "total_pages": 1,
    "total_platform_calls": {
        "2014-11": 3
    },
    "successful_platform_calls": {
        "2014-11": 3
    }
}
'''


PLATFORM_STATISTICS_USER_JSON_RESULT_EXAMPLE = '''
{
    "username": "test",
    "first_name": "",
    "last_name": "",
    "company_name": "",
    "email": "",
    "number_of_operations": 3,
    "successful_calls": {
        "201411": 3
    },
    "total_calls": {
        "201411": 3
    },
    "resource_uri": "/v2/platform_users/test/"
}
'''

PLATFORM_USERNAME_JSON_REQUEST_EXAMPLE = {
    "first_name": "Clark",
    "last_name": "Kent",
    "email": "test@test.com"
}

PLATFORM_USERNAME_WRONG_JSON_REQUEST_EXAMPLE = {
    "first_name": "Clark",
    "last_name": "Kent",
    "email": "XXXX"
}


PLATFORM_USERNAME_WRONG_RESULT = '''
{
    "error": {
        "message": "Validation Error",
        "code": "422",
        "type": "Unprocessable Entity",
        "description": {
            "email": [
                "Enter a valid email address."
            ]
        }
    }
}
'''


class PlatformTestCase(BasePlatformTestCase):

    def test_get_by_phone_without_platform_username(self):
        phone = 1231231231
        self.assertRaises(TypeError, self.client.get_by_phone, phone)

    def test_get_by_phone_with_platform_username(self):
        phone = 1231231231
        platform_user = 'test_username'
        self.patch_http_request(PHONE_JSON_RESULT_EXAMPLE)
        res = self.client.get_by_phone(phone, platform_username=platform_user)
        self.assertTrue(res['records'])
        self.assertEqual(res['records'][0]['email'], 'demo@nextcaller.com')
        self.assertEqual(res['records'][0]['first_name'], 'Jerry')
        self.assertEqual(res['records'][0]['last_name'], 'Seinfeld')

    def test_get_all_statistics(self):
        self.patch_http_request(PLATFORM_STATISTICS_JSON_RESULT_EXAMPLE)
        res = self.client.get_platform_statistics()
        self.assertTrue(res['successful_platform_calls'])
        self.assertTrue(res['total_platform_calls'])
        self.assertEqual(res['object_list'][0]['username'], 'test')
        self.assertEqual(res['object_list'][0]['number_of_operations'], 3)

    def test_get_users_statistics(self):
        self.patch_http_request(PLATFORM_STATISTICS_USER_JSON_RESULT_EXAMPLE)
        res = self.client.get_platform_user('test')
        self.assertEqual(res['username'], 'test')
        self.assertEqual(res['number_of_operations'], 3)

    def test_update_platform_user(self):
        platform_username = 'test_username'
        self.patch_http_request(self.fake_response)
        res = self.client.update_platform_user(
            platform_username, data=PLATFORM_USERNAME_JSON_REQUEST_EXAMPLE)
        self.assertEqual(res.status_code, 204)

    def test_update_wrong_platform_user(self):
        platform_username = 'test_username'
        fake_response = self.FakeResponse()
        fake_response.status_code = 400
        fake_response.content = PLATFORM_USERNAME_WRONG_RESULT
        self.patch_http_request(fake_response)
        res = self.client.update_platform_user(
            platform_username,
            data=PLATFORM_USERNAME_WRONG_JSON_REQUEST_EXAMPLE)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            json.loads(res.content)['error']['description']['email'][0],
            'Enter a valid email address.')


if __name__ == '__main__':
    unittest.main()
