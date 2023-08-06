"""
This file is part of FastPay.

 Copyright (c) 2015 Yahoo Japan Corporation

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""


class Card(object):

    def __init__(self, data):
        for k, v in data.items():
            self.__dict__[k] = v
