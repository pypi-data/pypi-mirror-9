"""
This file is part of FastPay.

 Copyright (c) 2015 Yahoo Japan Corporation

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from .error_handler import handle
from .errors import ConnectionError

import requests


class Client(object):

    def __init__(self, secret, api_base, timeout=3):
        self.__auth = (secret, '')
        self.__api_base = api_base
        self.__timeout = timeout

    def get(self, entrypoint=None):
        try:
            uri = self.__api_base + entrypoint
            r = requests.get(uri, auth=self.__auth, timeout=self.__timeout)
        except Exception as e:
            raise ConnectionError(str(e))

        return handle(r)

    def post(self, entrypoint=None, payload=None, headers=None):
        try:
            uri = self.__api_base + entrypoint
            r = requests.post(uri,
                              data=payload,
                              headers=headers,
                              auth=self.__auth,
                              timeout=self.__timeout)
        except Exception as e:
            raise ConnectionError(str(e))

        return handle(r)
