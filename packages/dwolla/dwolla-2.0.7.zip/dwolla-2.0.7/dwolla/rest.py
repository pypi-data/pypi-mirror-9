'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API

  Support is available on our forums at: https://discuss.dwolla.com/category/api-support

  Package -- Dwolla/dwolla-python
  Author -- Dwolla (David Stancu): api@dwolla.com, david@dwolla.com
  Copyright -- Copyright (C) 2014 Dwolla In
  License -- MIT
  Version -- 2.0.7
  Link -- http://developers.dwolla.com
'''

from . import constants as c
from .exceptions import * 

import json
import requests


class Rest(object):
    def __init__(self):
        """
        Constructor.

        :param settings: Dictionary with custom settings if
                         using _settings.py is not desired
        :return: None (__new__() returns the new instance ;))
        """

    @staticmethod
    def _parse(response):
        """
        Parses the Dwolla API response.

        :param response: Dictionary with content of API response.
        :return: Usually either a string or a dictionary depending
                 the on endpoint accesse
        """
        if response['Success'] is not True:
            raise DwollaAPIException("dwolla-python: An API error was encountered.\nServer Message:\n" + response['Message'], response['Message'])
        else:
            return response['Response']

    def _post(self, endpoint, params, custompostfix=False, dwollaparse=True):
        """
        Wrapper for requests' POST functionality.

        :param endpoint: String containing endpoint desire
        :param params: Dictionary containing parameters for request.
        :param custompostfix: String containing custom OAuth postfix (for special endpoints).
        :param dwollaparse: Boolean deciding whether or not to call self._parse().
        :return: Dictionary String containing endpoint desire containing API response.
        """
        try:
            resp = requests.post((c.sandbox_host if c.sandbox else c.production_host) + (custompostfix if custompostfix else c.default_postfix)
                                 + endpoint, json.dumps(params), proxies=c.proxy, timeout=c.rest_timeout,
                                 headers={'User-Agent': 'dwolla-python/2.x', 'Content-Type': 'application/json'})
        except Exception as e:
            if c.debug:
                print("dwolla-python: An error has occurred while making a POST request:\n" + e.message)
        else:
            return self._parse(json.loads(resp.text)) if dwollaparse else json.loads(resp.text)

    def _get(self, endpoint, params, dwollaparse=True):
        """
        Wrapper for requests' GET functionality.

        :param endpoint: String containing endpoint desire
        :param params: Dictionary containing parameters for request
        :param dwollaparse: Boolean deciding whether or not to call self._parse().
        :return: Dictionary String containing endpoint desire containing API response.
        """
        try:
            resp = requests.get((c.sandbox_host if c.sandbox else c.production_host) + c.default_postfix + endpoint, params=params, timeout=c.rest_timeout,
                                proxies=c.proxy, headers={'User-Agent': 'dwolla-python/2.x'})
        except Exception as e:
            if c.debug:
                print("dwolla-python: An error has occurred while making a GET request:\n" + e.message)
        else:
            return self._parse(json.loads(resp.text)) if dwollaparse else json.loads(resp.json())

r = Rest()
