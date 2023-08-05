from __future__ import unicode_literals
import json
import unittest
try:
    from .base import BaseTestCase, BasePlatformTestCase
except (ValueError, ImportError):
    from pynextcaller.tests.base import BaseTestCase, BasePlatformTestCase


PROFILE_JSON_REQUEST_EXAMPLE = {
    "first_name": "Clark",
    "last_name": "Kent",
    "shipping_address1": {
        "line1": "225 Kryptonite Ave.",
        "line2": "",
        "city": "Smallville",
        "state": "KS",
        "zip_code": "66002"
    }
}

PROFILE_JSON_WRONG_REQUEST_EXAMPLE = {
    "first_name": "Clark",
    "last_name": "Kent",
    "email": "XXXXXXXXXXXX",
    "shipping_address1": {
        "line1": "225 Kryptonite Ave.",
        "line2": "",
        "city": "Smallville",
        "state": "KS",
        "zip_code": "66002"
    }
}

PROFILE_JSON_RESULT_EXAMPLE = '''
{
    "id": "97d949a413f4ea8b85e9586e1f2d9a",
    "first_name": "Jerry",
    "last_name": "Seinfeld",
    "name": "Jerry Seinfeld",
    "language": "English",
    "fraud_threat": "low",
    "spoof": "false",
    "phone": [
        {
            "number": "2125558383",
            "carrier": "Verizon Wireless",
            "line_type": "LAN"
        }
    ],
    "address": [
        {
            "city": "New York",
            "extended_zip": "",
            "country": "USA",
            "line2": "Apt 5a",
            "line1": "129 West 81st Street",
            "state": "NY",
            "zip_code": "10024"
        }
    ],
    "email": "demo@nextcaller.com",
    "social_links": [
        {
            "followers": 1,
            "type": "twitter",
            "url": "https://twitter.com/nextcaller"
        },
        {
            "type": "facebook",
            "url": "https://www.facebook.com/nextcaller"
        },
        {
            "type": "linkedin",
            "url": "https://www.linkedin.com/company/next-caller"
        }
    ],
    "age": "45-54",
    "gender": "Male",
    "household_income": "50k-75k",
    "marital_status": "Single",
    "presence_of_children": "No",
    "home_owner_status": "Rent",
    "market_value": "350k-500k",
    "length_of_residence": "12 Years",
    "high_net_worth": "No",
    "occupation": "Entertainer",
    "education": "Completed College",
    "department": "not specified"
}
'''

PROFILE_JSON_WRONG_RESULT = '''
{
    "error": {
        "message": "There are validation errors",
        "code": "1054",
        "type": "Validation",
        "description": {
            "email": [
                "Invalid email address"
            ]
        }
    }
}
'''


class ProfileTestCase(BaseTestCase):

    def test_profile_get_request(self):
        profile_id = '97d949a413f4ea8b85e9586e1f2d9a'
        self.patch_http_request(PROFILE_JSON_RESULT_EXAMPLE)
        res = self.client.get_by_profile_id(profile_id)
        self.assertEqual(res['email'], 'demo@nextcaller.com')
        self.assertEqual(res['first_name'], 'Jerry')
        self.assertEqual(res['last_name'], 'Seinfeld')

    def test_profile_update_request(self):
        profile_id = '97d949a413f4ea8b85e9586e1f2d9a'
        self.patch_http_request(self.fake_response)
        res = self.client.update_by_profile_id(
            profile_id, data=PROFILE_JSON_REQUEST_EXAMPLE)
        self.assertEqual(res.status_code, 204)

    def test_profile_update_wrong_request(self):
        profile_id = '97d949a413f4ea8b85e9586e1f2d9a'
        fake_response = self.FakeResponse()
        fake_response.status_code = 400
        fake_response.content = PROFILE_JSON_WRONG_RESULT
        self.patch_http_request(fake_response)
        res = self.client.update_by_profile_id(
            profile_id, data=PROFILE_JSON_WRONG_REQUEST_EXAMPLE)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            json.loads(res.content)['error']['description']['email'][0],
            'Invalid email address')


class PlatformProfileTestCase(BasePlatformTestCase):

    def test_profile_get_request(self):
        profile_id = '97d949a413f4ea8b85e9586e1f2d9a'
        self.patch_http_request(PROFILE_JSON_RESULT_EXAMPLE)
        res = self.client.get_by_profile_id(profile_id, self.platform_username)
        self.assertEqual(res['email'], 'demo@nextcaller.com')
        self.assertEqual(res['first_name'], 'Jerry')
        self.assertEqual(res['last_name'], 'Seinfeld')

    def test_profile_update_request(self):
        profile_id = '97d949a413f4ea8b85e9586e1f2d9a'
        self.patch_http_request(self.fake_response)
        res = self.client.update_by_profile_id(
            profile_id, PROFILE_JSON_REQUEST_EXAMPLE, self.platform_username)
        self.assertEqual(res.status_code, 204)

    def test_profile_update_wrong_request(self):
        profile_id = '97d949a413f4ea8b85e9586e1f2d9a'
        fake_response = self.FakeResponse()
        fake_response.status_code = 400
        fake_response.content = PROFILE_JSON_WRONG_RESULT
        self.patch_http_request(fake_response)
        res = self.client.update_by_profile_id(
            profile_id, PROFILE_JSON_WRONG_REQUEST_EXAMPLE,
            self.platform_username)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            json.loads(res.content)['error']['description']['email'][0],
            'Invalid email address')


if __name__ == '__main__':
    unittest.main()
