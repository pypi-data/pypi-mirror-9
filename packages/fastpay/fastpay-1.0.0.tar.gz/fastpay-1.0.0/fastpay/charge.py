"""
This file is part of FastPay.

 Copyright (c) 2015 Yahoo Japan Corporation

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from .compat import quote
from .card import Card
from .refund import Refund


class Charge(object):

    __api_entry = '/v1/charges'

    __api = None

    def __init__(self, api, data=None):
        if api is None:
            raise RuntimeError('api is none')

        self.__api = api
        if data is not None:
            self._append_data(data)

    def create(self, amount, card, description=None, capture=True):
        payload = {
            "amount": amount,
            "card": card,
            "description": description,
            "capture": 'true' if capture else 'false'
        }

        data = self.__api.post(self.__api_entry, payload)

        return Charge(self.__api, data)

    def capture(self):
        entrypoint = self.__api_entry + "/" + quote(self.id, safe='') + "/capture"
        data = self.__api.post(entrypoint, {}, headers={'Content-Length': 0})
        self._append_data(data)

    def refund(self, amount=None):
        entrypoint = self.__api_entry + "/" + quote(self.id, safe='') + "/refund"
        if amount is None:
            data = self.__api.post(entrypoint, {}, headers={'Content-Length': 0})
        else:
            data = self.__api.post(entrypoint, {"amount": amount})

        self._append_data(data)

    def retrieve(self, charge_id):
        uri = self.__api_entry + "/" + quote(charge_id, safe='')
        data = self.__api.get(uri)

        return Charge(self.__api, data)

    def all(self, count=10, offset=0):
        uri = self.__api_entry + "?count=" + str(count) + "&offset=" + str(offset)
        data = self.__api.get(uri)

        return [Charge(self.__api, charge_data) for charge_data in data]

    def _append_data(self, data):
        for k, v in data.items():
            if k == 'card':
                self.__dict__[k] = Card(v)
            elif k == 'refunds':
                refunds = []
                for refund in v:
                    refunds.append(Refund(refund))

                self.__dict__[k] = refunds
            else:
                self.__dict__[k] = v
