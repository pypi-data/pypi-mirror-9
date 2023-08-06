"""
This file is part of FastPay.

 Copyright (c) 2015 Yahoo Japan Corporation

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from .errors import FastPayError, ConnectionError, ApiError, InvalidRequestError, CardError

import requests


def handle(r):
    try:
        data = r.json()
    except ValueError:
        raise ConnectionError("json parse failed.", r.status_code, r.text)
    except:
        raise FastPayError("system error", r.status_code, r.text)

    if not requests.codes.ok <= r.status_code <= requests.codes.im_used:
        _raise_error(r, data)

    try:
        object = data['object']
    except KeyError:
        raise FastPayError("invalid stracture.", r.status_code, r.text)

    if object == 'list':
        try:
            data = data['data']
        except KeyError:
            raise FastPayError("invalid stracture.", r.status_code, r.text)

    return data


def _raise_error(r, data):
    try:
        error = data['error']
        error_type = error['type']
        error_code = error['code']
        message = error['message']
    except KeyError:
        raise FastPayError("invalid structure.", r.status_code, r.text)

    if error_type == 'card_error':
        raise CardError(message, r.status_code, r.text, error_code)
    elif error_type == 'api_error':
        raise ApiError(message, r.status_code, r.text)
    elif error_type == 'invalid_request_error':
        raise InvalidRequestError(message, r.status_code, r.text)
    else:
        raise FastPayError(message, r.status_code, r.text)
