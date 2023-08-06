# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Originally part of Zato - open-source ESB, SOA, REST, APIs and cloud integrations in Python
# https://zato.io

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from uuid import uuid4

# setuptools
from pkg_resources import get_distribution

version = get_distribution('zato-apitest').version

INVALID = 'invalid-{}'.format(uuid4().hex)
NO_VALUE = 'no-value-{}'.format(uuid4().hex)

class AUTH:
    BASIC_AUTH = 'basic-auth'
