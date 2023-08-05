import unittest

from dwolla import contacts, constants
from mock import MagicMock


class ContactsTest(unittest.TestCase):
    def setUp(self):
        contacts.r._get = MagicMock()
        contacts.r._post = MagicMock()
        constants.client_id = "SOME ID"
        constants.client_secret = "SOME ID"
        constants.access_token = "AN OAUTH TOKEN"

    def testget(self):
        contacts.get({'a': 'parameter'})
        contacts.r._get.assert_any_call('/contacts', {'a': 'parameter', 'oauth_token': 'AN OAUTH TOKEN'})

    def testnearby(self):
        contacts.nearby(45, 50, {'another': 'parameter'})
        contacts.r._get.assert_any_call('/contacts/nearby', {'latitude': 45, 'client_secret': 'SOME ID', 'another': 'parameter', 'client_id': 'SOME ID', 'longitude': 50})

if __name__ == '__main__':
    unittest.main()