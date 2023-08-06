'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  This file contains functionality for all accounts related endpoints.
'''

from . import constants as c
from .rest import r

def basic(aid):
    """
    Returns basic account info for the passed account ID.

    :param aid: String of account ID.
    :return: Dictionary with account information.
    """
    if not aid:
        raise Exception('basic() requires aid parameter')


    return r._get('/users/' + aid,
                     {
                         'client_id': c.client_id,
                         'client_secret': c.client_secret
                     })

def full(alternate_token=False):
    """
    Returns full account information for the user associated
    with the currently set OAuth token.

    :return: Dictionary with account information.
    """
    return r._get('/users',
                     {
                         'oauth_token': alternate_token if alternate_token else c.access_token
                     })

def balance(alternate_token=False):
    """
    Gets balance for the account associated with the
    currently set OAuth token.

    :return: Balance
    """
    return r._get('/balance', {'oauth_token': alternate_token if alternate_token else c.access_token})

def nearby(lat, lon):
    """
    Returns users and venues near a location.

    :param lat: Double containing latitude.
    :param lon: Double containing longitude.
    :return: Dictionary with venues and users.
    """
    if not lat:
        raise Exception('nearby() requires lat parameter')
    if not lon:
        raise Exception('nearby() requires lon parameter')

    return r._get('/users/nearby',
                     {
                         'client_id': c.client_id,
                         'client_secret': c.client_secret,
                         'latitude': lat,
                         'longitude': lon
                     })

def autowithdrawalstatus(alternate_token=False):
    """
    Gets auto withdrawal status for the account associated
    with the currently set OAuth token.
    :return: AW status for account.
    """
    return r._get('/accounts/features/auto_withdrawl',
                  {
                      'oauth_token': alternate_token if alternate_token else c.access_token
                  })

def toggleautowithdrawalstatus(status, fid, alternate_token=False):
    """
    Sets auto-withdrawal status of the account associated
    with the current OAuth token under the specified
    funding ID.
    :param status: Boolean for toggle.
    :param fid: String with funding ID for target account
    :return: String (Either "Enabled" or "Disabled")
    """
    if not status:
        raise Exception('toggleautowithdrawlstatus() requires status parameter')
    if not fid:
        raise Exception('toggleautowithdrawlstatus() requires fid parameter')

    return r._post('/accounts/features/auto_withdrawl',
                   {
                       'oauth_token': alternate_token if alternate_token else c.access_token,
                       'enabled': status,
                       'fundingId': fid
                   })



