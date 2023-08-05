import unittest

from dwolla import fundingsources, constants
from mock import MagicMock


class FundingSourcesTest(unittest.TestCase):
    def setUp(self):
        fundingsources.r._get = MagicMock()
        fundingsources.r._post = MagicMock()
        constants.client_id = "SOME ID"
        constants.client_secret = "SOME ID"
        constants.access_token = "AN OAUTH TOKEN"
        constants.pin = 1234

    def testinfo(self):
        fundingsources.info('123456')
        fundingsources.r._get.assert_any_call('/fundingsources/123456', {'oauth_token': 'AN OAUTH TOKEN'})

    def testget(self):
        fundingsources.get({'a': 'parameter'})
        fundingsources.r._get.assert_any_call('/fundingsources', {'a': 'parameter', 'oauth_token': 'AN OAUTH TOKEN'})

    def testadd(self):
        fundingsources.add('123456', '654321', 'Checking', 'Unit Test Bank')
        fundingsources.r._post.assert_any_call('/fundingsources', {'routing_number': '654321', 'account_type': 'Checking', 'oauth_token': 'AN OAUTH TOKEN', 'account_number': '123456', 'account_name': 'Unit Test Bank'})

    def testverify(self):
        fundingsources.verify(0.03, 0.02, '123456')
        fundingsources.r._post.assert_any_call('/fundingsources/123456', {'deposit2': 0.02, 'oauth_token': 'AN OAUTH TOKEN', 'deposit1': 0.03})

    def testwithdraw(self):
        fundingsources.withdraw(20.50, '123456')
        fundingsources.r._post.assert_any_call('/fundingsources/123456/withdraw', {'amount': 20.5, 'oauth_token': 'AN OAUTH TOKEN', 'pin': 1234})

    def testdeposit(self):
        fundingsources.deposit(30.50, '123456')
        fundingsources.r._post.assert_any_call('/fundingsources/123456/deposit', {'amount': 30.5, 'oauth_token': 'AN OAUTH TOKEN', 'pin': 1234})


if __name__ == '__main__':
    unittest.main()
