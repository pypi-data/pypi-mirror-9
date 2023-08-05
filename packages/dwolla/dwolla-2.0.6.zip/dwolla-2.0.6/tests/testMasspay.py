import unittest

from dwolla import masspay, constants
from mock import MagicMock


class MassPayTest(unittest.TestCase):
    def setUp(self):
        masspay.r._get = MagicMock()
        masspay.r._post = MagicMock()
        constants.client_id = "SOME ID"
        constants.client_secret = "SOME ID"
        constants.access_token = "AN OAUTH TOKEN"
        constants.pin = 1234

    def testcreate(self):
        masspay.create('Balance', {frozenset({'amount': 10.00, 'destination': '812-123-1111'})})
        masspay.r._post.assert_any_call('/masspay', {'fundsSource': 'Balance', 'items': set([frozenset(['amount', 'destination'])]), 'oauth_token': 'AN OAUTH TOKEN', 'pin': 1234})

    def testgetjob(self):
        masspay.getjob('123456')
        masspay.r._get.assert_any_call('/masspay/123456', {'oauth_token': 'AN OAUTH TOKEN'})

    def testgetjobitems(self):
        masspay.getjobitems('1234567', {'a': 'parameter'})
        masspay.r._get.assert_any_call('/masspay/1234567/items', {'a': 'parameter', 'oauth_token': 'AN OAUTH TOKEN'})

    def testgetitem(self):
        masspay.getitem('123', '456')
        masspay.r._get.assert_any_call('/masspay/123/items/456', {'oauth_token': 'AN OAUTH TOKEN'})

    def testlistjobs(self):
        masspay.listjobs()
        masspay.r._get.assert_any_call('/masspay', {'oauth_token': 'AN OAUTH TOKEN'})

if __name__ == '__main__':
    unittest.main()
