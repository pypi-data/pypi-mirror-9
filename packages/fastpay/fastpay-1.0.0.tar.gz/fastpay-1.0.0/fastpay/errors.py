"""
This file is part of FastPay.

 Copyright (c) 2015 Yahoo Japan Corporation

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""


class FastPayError(Exception):
    INCORRECT_NUMBER = "incorrect_number"
    INVALID_NUMBER = "invalid_number"
    INVALID_EXPIRY_MONTH = "invalid_expiry_year"
    INVALID_CVC = "invalid_cvc"
    EXPIRED_CARD = "expired_card"
    INCORRECT_CVC = "incorrect_cvc"
    CARD_DECLINED = "card_declined"

    def __init__(self, message, status=None, body=None):
        if status is None:
            status = -1

        error_message = '[%s] %s, status: %d, body: %s' % \
                        (self.__class__.__name__, message, status, body)
        Exception.__init__(self, error_message)
        self.status = status
        self.body = body


class ConnectionError(FastPayError):
    pass


class ApiError(FastPayError):
    pass


class InvalidRequestError(FastPayError):
    pass


class CardError(FastPayError):

    def __init__(self, message, status, body, code):
        FastPayError.__init__(self, message, status, body)
        self.code = code
