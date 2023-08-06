"""
This file is part of FastPay.

 Copyright (c) 2015 Yahoo Japan Corporation

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from .client import Client
from .charge import Charge
from .subscription import Subscription


class FastPay(object):
    """FastPay Client Library

    usage:

        Create a new charge (auto captured)

        >>> from fastpay import FastPay
        >>> fastpay = FastPay(SEACRET_ID)
        >>> charge = fastpay.charge.create(
                amount=400,
                card="token",
                description="test description",
                capture=True
                )


    ... or Retrieve a Charge

        >>> from fastpay import FastPay
        >>> fastpay = FastPay(SEACRET_ID)
        >>> charge = fastpay.charge.retrieve(CHARGE_ID)

    ... or Refund a Charge

        >>> from fastpay import FastPay
        >>> fastpay = FastPay(SEACRET_ID)
        >>> charge = fastpay.charge.retrieve(CHARGE_ID)
        >>> charge.refund()

    ... or Partial Refund a Charge

        >>> from fastpay import FastPay
        >>> fastpay = FastPay(SEACRET_ID)
        >>> charge = fastpay.charge.retrieve(CHARGE_ID)
        >>> charge.refund(500)

    ... or Capture a Charge

        >>> from fastpay import FastPay
        >>> fastpay = FastPay(SEACRET_ID)
        >>> charge = fastpay.charge.create(
                amount=400,
                card="token",
                description="test description",
                capture=False
                )
        >>> charge.capture()

    ... or List all charges

        >>> from fastpay import FastPay
        >>> fastpay = FastPay(SEACRET_ID)
        >>> charge_list = fastpay.charge.all(count=10)

    ... or activate subscription

        >>> from fastpay import FastPay
        >>> fastpay = FastPay(SEACRET_ID)
        >>> subscription = fastpay.subscription.activate(SUBSCRIPTION_ID)

    ... or cancel subscription

        >>> from fastpay import FastPay
        >>> fastpay = FastPay(SEACRET_ID)
        >>> subscription = fastpay.subscription.cancel(SUBSCRIPTION_ID)
    """

    charge = None
    subscription = None

    def __init__(self, secret, timeout=60, api_base='https://fastpay.yahooapis.jp'):
        """Initialize

        Keyword arguments:
        secret -- Fastpay secret id
        timeout -- Request timeout (default 60)
        api_base -- request URI (default https://fastpay.yahooapis.jp)

        """
        client = Client(secret, api_base, timeout)
        self.charge = Charge(client)
        self.subscription = Subscription(client)
