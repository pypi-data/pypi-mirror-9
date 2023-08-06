"""
This file is part of FastPay.

 Copyright (c) 2015 Yahoo Japan Corporation

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""


try:
    from urllib.parse import quote  # noqa
except ImportError:
    from urllib import quote  # noqa
