import unittest

from dwolla import accounts, constants
from mock import MagicMock


class AccountsTest(unittest.TestCase):
    def setUp(self):
        accounts.r._get = MagicMock()
        accounts.r._post = MagicMock()
        constants.client_id = "SOME ID"
        constants.client_secret = "SOME ID"
        constants.access_token = "AN OAUTH TOKEN"

    def testbasic(self):
        accounts.basic('123456')
        accounts.r._get.assert_any_call('/users/123456', {'client_secret': 'SOME ID', 'client_id': 'SOME ID'})

    def testfull(self):
        accounts.full()
        accounts.r._get.assert_any_call('/users', {'oauth_token': 'AN OAUTH TOKEN'})

    def testbalance(self):
        accounts.balance()
        accounts.r._get.assert_any_call('/balance', {'oauth_token': 'AN OAUTH TOKEN'})

    def testnearby(self):
        accounts.nearby(45, 50)
        accounts.r._get.assert_any_call('/users/nearby', {'latitude': 45, 'client_secret': 'SOME ID', 'longitude': 50, 'client_id': 'SOME ID'})

    def testautowithdrawalstatus(self):
        accounts.autowithdrawalstatus()
        accounts.r._get.assert_any_call('/accounts/features/auto_withdrawl', {'oauth_token': 'AN OAUTH TOKEN'})

    def testtoggleautowithdrawalstatus(self):
        accounts.toggleautowithdrawalstatus(True, '123456')
        accounts.r._post.assert_any_call('/accounts/features/auto_withdrawl', {'enabled': True, 'oauth_token': 'AN OAUTH TOKEN', 'fundingId': '123456'})


if __name__ == '__main__':
    unittest.main()