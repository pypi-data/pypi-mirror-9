'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  This file contains functionality for all transactions related endpoints.
'''

from . import constants as c
from .rest import r


def send(destinationid, amount, params=False, alternate_token=False, alternate_pin=False):
    """
    Sends money to the specified destination user.

    :param destinationid: String of Dwolla ID to send funds to.
    :param amount: Double of amount to sen
    :param params: Dictionary of additional parameters
    :return: Integer of transaction ID
    """
    if not destinationid:
        raise Exception('send() requires destinationid parameter')
    if not amount:
        raise Exception('send() requires amount parameter')

    p = {
        'oauth_token': alternate_token if alternate_token else c.access_token,
        'pin': alternate_pin if alternate_pin else c.pin,
        'destinationId': destinationid,
        'amount': amount
    }

    if params:
        p = dict(list(p.items()) + list(params.items()))

    return r._post('/transactions/send', p)


def get(params=False, alternate_token=False):
    """
    Lists transactions for the user associated with
    the currently set OAuth token.

    :param params: Dictionary with additional parameters
    :return: Dictionary with transactions
    """
    p = {
        'oauth_token': alternate_token if alternate_token else c.access_token,
        'client_id': c.client_id,
        'client_secret': c.client_secret
    }

    if params:
        p = dict(list(p.items()) + list(params.items()))

    return r._get('/transactions', p)


def info(tid, alternate_token=False):
    """
    Returns transaction information for the transaction
    associated with the passed transaction ID

    :param id: String with transaction ID.
    :return: Dictionary with information about transaction.
    """
    if not tid:
        raise Exception('info() requires id parameter')

    return r._get('/transactions/' + tid,
                  {
                      'oauth_token': alternate_token if alternate_token else c.access_token,
                      'client_id': c.client_id,
                      'client_secret': c.client_secret
                  })


def refund(tid, fundingsource, amount, params=False, alternate_token=False, alternate_pin=False):
    """
    Refunds (either completely or partially) funds to
    the sending user for a transaction.

    :param id: String with transaction ID.
    :param fundingsource: String with funding source for refund transaction.
    :param amount: Double with amount to refun
    :param params: Dictionary with additional parameters.
    :return: Dictionary with information about refund transaction.
    """
    if not tid:
        raise Exception('refund() requires parameter id')
    if not fundingsource:
        raise Exception('refund() requires parameter fundingsource')
    if not amount:
        raise Exception('refund() requires parameter amount')

    p = {
        'oauth_token': alternate_token if alternate_token else c.access_token,
        'pin': alternate_pin if alternate_pin else c.pin,
        'fundsSource': fundingsource,
        'transactionId': tid,
        'amount': amount
    }

    if params:
        p = dict(list(p.items()) + list(params.items()))

    return r._post('/transactions/refund', p)


def stats(params=False, alternate_token=False):
    """
    Retrieves transaction statistics for
    the user associated with the current OAuth token.

    :param params: Dictionary with additional parameters
    :return: Dictionary with transaction statistics
    """
    p = {'oauth_token': alternate_token if alternate_token else c.access_token}

    if params:
        p = dict(list(p.items()) + list(params.items()))

    return r._get('/transactions/stats', p)
