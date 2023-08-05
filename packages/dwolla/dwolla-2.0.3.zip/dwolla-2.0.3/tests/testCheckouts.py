import unittest
from dwolla import checkouts, constants
from mock import MagicMock


class CheckoutsTest(unittest.TestCase):
    def setUp(self):
        checkouts.r._get = MagicMock()
        checkouts.r._post = MagicMock()

        checkouts.r._post.return_value = dict({'CheckoutId': 'TEST'})

        constants.client_id = "SOME ID"
        constants.client_secret = "SOME ID"
        constants.access_token = "AN OAUTH TOKEN"
        constants.pin = 1234

    def testcreate(self):
        checkouts.create({
            'orderItems': {
                frozenset({
                    'name': 'Prime Rib Sandwich',
                    'description': 'A somewhat tasty non-vegetarian sandwich',
                    'quantity': '1',
                    'price': '15.00'
                })
            },
            'destinationId': '812-740-4294',
            'total': 15.00,
            'notes': 'blahhh',
            'metadata': frozenset({
                'key1': 'something',
                'key2': 'another thing'
            })})
        checkouts.r._post.assert_any_call('/offsitegateway/checkouts', {'client_secret': 'SOME ID', 'purchaseOrder': {'destinationId': '812-740-4294', 'total': 15.0, 'notes': 'blahhh', 'orderItems': set([frozenset(['price', 'description', 'name', 'quantity'])]), 'metadata': frozenset(['key2', 'key1'])}, 'client_id': 'SOME ID'})

    def testget(self):
        checkouts.get('123456')
        checkouts.r._get.assert_any_call('/offsitegateway/checkouts/123456', {'client_secret': 'SOME ID', 'client_id': 'SOME ID'})

    def testcomplete(self):
        checkouts.complete('123456')
        checkouts.r._get.assert_any_call('/offsitegateway/checkouts/123456/complete', {'client_secret': 'SOME ID', 'client_id': 'SOME ID'})

if __name__ == '__main__':
    unittest.main()