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


PHONE_JSON_RESULT_EXAMPLE = '''
{
    "records": [
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
    ]
}
'''


class PhoneTestCase(BaseTestCase):

    def test_by_short_phone(self):
        phone = '212555838'
        self.patch_http_request(PHONE_JSON_RESULT_EXAMPLE)
        self.assertRaises(ValueError, self.client.get_by_phone, phone)

    def test_by_wrong_phone(self):
        phone = 'XXXXXXXXXX'
        self.patch_http_request(PHONE_JSON_RESULT_EXAMPLE)
        self.assertRaises(ValueError, self.client.get_by_phone, phone)

    def test_by_wrong_argument(self):
        phone = '1231231231'
        self.patch_http_request(PHONE_JSON_RESULT_EXAMPLE)
        self.assertRaises(ValueError, self.client.get_by_phone, phone, x='xx')

    def test_by_phone(self):
        phone = '2125558383'
        self.patch_http_request(PHONE_JSON_RESULT_EXAMPLE)
        res = self.client.get_by_phone(phone)
        self.assertTrue(res['records'])
        self.assertEqual(res['records'][0]['email'], 'demo@nextcaller.com')
        self.assertEqual(res['records'][0]['first_name'], 'Jerry')
        self.assertEqual(res['records'][0]['last_name'], 'Seinfeld')


class PlatformPhoneTestCase(BasePlatformTestCase):

    def test_by_short_phone(self):
        phone = '212555838'
        self.patch_http_request(PHONE_JSON_RESULT_EXAMPLE)
        self.assertRaises(ValueError, self.client.get_by_phone,
                          phone, self.platform_username)

    def test_by_wrong_phone(self):
        phone = 'XXXXXXXXXX'
        self.patch_http_request(PHONE_JSON_RESULT_EXAMPLE)
        self.assertRaises(ValueError, self.client.get_by_phone,
                          phone, self.platform_username)

    def test_by_wrong_argument(self):
        phone = '1231231231'
        self.patch_http_request(PHONE_JSON_RESULT_EXAMPLE)
        self.assertRaises(ValueError, self.client.get_by_phone, phone,
                          self.platform_username, x='xx')

    def test_by_phone(self):
        phone = '2125558383'
        self.patch_http_request(PHONE_JSON_RESULT_EXAMPLE)
        res = self.client.get_by_phone(phone, self.platform_username)
        self.assertTrue(res['records'])
        self.assertEqual(res['records'][0]['email'], 'demo@nextcaller.com')
        self.assertEqual(res['records'][0]['first_name'], 'Jerry')
        self.assertEqual(res['records'][0]['last_name'], 'Seinfeld')


if __name__ == '__main__':
    unittest.main()
