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


ADDRESS_JSON_RESULT_EXAMPLE = '''
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

WRONG_ADDRESS_DATA = {
    'first_name': 'Jerry',
    'last_name': 'Seinfeld',
    'address': '129 West 81st Street',
    'city': 'New York',
}


WRONG_ADDRESS_ZIP_DATA = {
    'first_name': 'Jerry',
    'last_name': 'Seinfeld',
    'address': '129 West 81st Street',
    'city': 'New York',
    'state': 'NY',
    'zip_code': '1002',
}


WRONG_ADDRESS_FIELDS_DATA = {
    'first_name': 'Jerry',
    'last_name': 'Seinfeld',
    'address': '129 West 81st Street',
    'city': 'New York',
    'state': 'NY',
    'zip_code': '10024',
    'test_field': 'xx',
}


ADDRESS_DATA = {
    'first_name': 'Jerry',
    'last_name': 'Seinfeld',
    'address': '129 West 81st Street',
    'city': 'New York',
    'state': 'NY',
    'zip_code': '10024',
}


class AddressTestCase(BaseTestCase):

    def test_address_by_not_full_address(self):
        self.patch_http_request(ADDRESS_JSON_RESULT_EXAMPLE)
        self.assertRaises(
            ValueError, self.client.get_by_address_name, WRONG_ADDRESS_DATA)

    def test_address_by_wrong_zip(self):
        self.patch_http_request(ADDRESS_JSON_RESULT_EXAMPLE)
        self.assertRaises(
            ValueError, self.client.get_by_address_name, WRONG_ADDRESS_ZIP_DATA)

    def test_address_by_wrong_fields(self):
        self.patch_http_request(ADDRESS_JSON_RESULT_EXAMPLE)
        self.assertRaises(
            ValueError, self.client.get_by_address_name, WRONG_ADDRESS_FIELDS_DATA)

    def test_by_address(self):
        self.patch_http_request(ADDRESS_JSON_RESULT_EXAMPLE)
        res = self.client.get_by_address_name(ADDRESS_DATA)
        self.assertTrue(res['records'])
        self.assertEqual(res['records'][0]['email'], 'demo@nextcaller.com')
        self.assertEqual(res['records'][0]['first_name'], 'Jerry')
        self.assertEqual(res['records'][0]['last_name'], 'Seinfeld')


class PlatformAddressTestCase(BasePlatformTestCase):

    def test_address_by_not_full_address(self):
        self.patch_http_request(ADDRESS_JSON_RESULT_EXAMPLE)
        self.assertRaises(
            ValueError, self.client.get_by_address_name,
            WRONG_ADDRESS_DATA, self.platform_username)

    def test_address_by_wrong_zip(self):
        self.patch_http_request(ADDRESS_JSON_RESULT_EXAMPLE)
        self.assertRaises(
            ValueError, self.client.get_by_address_name,
            WRONG_ADDRESS_ZIP_DATA, self.platform_username)

    def test_address_by_wrong_fields(self):
        self.patch_http_request(ADDRESS_JSON_RESULT_EXAMPLE)
        self.assertRaises(
            ValueError, self.client.get_by_address_name,
            WRONG_ADDRESS_FIELDS_DATA, self.platform_username)

    def test_by_address(self):
        self.patch_http_request(ADDRESS_JSON_RESULT_EXAMPLE)
        res = self.client.get_by_address_name(ADDRESS_DATA, self.platform_username)
        self.assertTrue(res['records'])
        self.assertEqual(res['records'][0]['email'], 'demo@nextcaller.com')
        self.assertEqual(res['records'][0]['first_name'], 'Jerry')
        self.assertEqual(res['records'][0]['last_name'], 'Seinfeld')


if __name__ == '__main__':
    unittest.main()
