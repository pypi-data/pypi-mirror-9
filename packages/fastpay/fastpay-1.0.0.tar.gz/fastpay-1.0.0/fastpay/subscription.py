"""
This file is part of FastPay.

 Copyright (c) 2015 Yahoo Japan Corporation

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from .compat import quote
from .plan import Plan


class Subscription(object):

    __api_entry = '/v1/subscription'

    __api = None

    def __init__(self, api, data=None):
        if api is None:
            raise RuntimeError('api is none')

        self.__api = api
        if data is not None:
            self._append_data(data)

    def activate(self, subscription_id=None):
        if subscription_id is None:
            id = self.id
        else:
            id = subscription_id

        entrypoint = self.__api_entry + "/" + quote(id, safe='') + "/activate"
        data = self.__api.post(entrypoint, {}, headers={'Content-Length': 0})
        self._append_data(data)

        return self

    def cancel(self, subscription_id=None):
        if subscription_id is None:
            id = self.id
        else:
            id = subscription_id

        entrypoint = self.__api_entry + "/" + quote(id, safe='') + "/cancel"
        data = self.__api.post(entrypoint, {}, headers={'Content-Length': 0})
        self._append_data(data)

        return self

    def _append_data(self, data):
        for k, v in data.items():
            if k == 'plan':
                self.__dict__[k] = Plan(v)
            else:
                self.__dict__[k] = v
