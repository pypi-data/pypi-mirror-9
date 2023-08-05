'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  This file contains functionality for all requests related endpoints.
'''

from . import constants as c
from .rest import r


def create(sourceid, amount, params=False, alternate_token=False):
    """
    Requests money from a user for a user associated with
    the current OAuth token.

    :param sourceid: String with Dwolla ID to request funds from.
    :param amount: Double with amount to request.
    :param params: Dictionary with additional parameters.
    :return: Integer with Request ID of submitted request.
    """
    if not sourceid:
        raise Exception('create() requires sourceid parameter')
    if not amount:
        raise Exception('create() requires amount parameter')

    p = {
        'oauth_token': alternate_token if alternate_token else c.access_token,
        'sourceId': sourceid,
        'amount': amount
    }

    if params:
        p = dict(list(p.items()) + list(params.items()))

    return r._post('/requests/', p)


def get(params=False, alternate_token=False):
    """
    Retrieves a list of pending money requests for the user
    associated with the current OAuth token.

    :param params: Dictionary with additional parameters.
    :return: Dictionary with pending money requests and relevant data.
    """
    p = {'oauth_token': alternate_token if alternate_token else c.access_token}

    if params:
        p = dict(list(p.items()) + list(params.items()))

    return r._get('/requests', params=p)


def info(requestid, alternate_token=False):
    """
    Retrieves additional information about a pending money
    request.

    :param requestid: String with Request ID to retrieve info for.
    :return: Dictionary with information relevant to the request.
    """
    if not requestid:
        raise Exception('info() requires requestid parameter')

    return r._get('/requests/' + requestid, params={'oauth_token': alternate_token if alternate_token else c.access_token})


def cancel(requestid, alternate_token=False):
    """
    Cancels a pending money request.

    :param requestid: String with Request ID to cancel.
    :return: None
    """
    if not requestid:
        raise Exception('cancel() requires requestid parameter')

    return r._post('/requests/' + requestid + '/cancel/', params={'oauth_token': alternate_token if alternate_token else c.access_token})


def fulfill(requestid, amount, params=False, alternate_token=False, alternate_pin=False):
    """
    Fulfills a pending money request.

    :param requestid: String with Request ID to fulfill.
    :param amount: Double with amount to fulfill.
    :param params: Dictionary with additional parameters.
    :return: Dictionary with information (transaction/request IDs) relevant to fulfilled request.
    """
    if not requestid:
        raise Exception('fulfill() requires requestid parameter')
    if not amount:
        raise Exception('fulfill() requires amount parameter')

    p = {'oauth_token': alternate_token if alternate_token else c.access_token,
         'amount': amount,
         'pin': alternate_pin if alternate_pin else c.pin}

    if params:
        p = dict(list(p.items()) + list(params.items()))

    return r._post('/requests/' + requestid + '/fulfill', p)