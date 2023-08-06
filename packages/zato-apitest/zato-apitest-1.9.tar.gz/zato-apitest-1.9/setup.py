# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Originally part of Zato - open-source ESB, SOA, REST, APIs and cloud integrations in Python
# https://zato.io

from __future__ import absolute_import, division, print_function, unicode_literals

import os
from setuptools import setup, find_packages

version = '1.9'

LONG_DESCRIPTION = """
zato-apitest is a friendly command line tool for creating beautiful tests of HTTP-based REST, XML and SOAP APIs with as little
hassle as possible.

Tests are written in plain English, with no programming needed, and can be trivially easy extended in Python if need be.

Note that zato-apitest is meant to test APIs only. It's doesn't simulate a browser nor any sort of user interactions. It's meant
purely for machine-machine API testing.

Originally part of `Zato <https://zato.io>`_ - open-source ESB, SOA, REST, APIs and cloud integrations in Python.

In addition to HTTP Zato itself supports AMQP, ZeroMQ, WebSphere MQ, including JMS, Redis, FTP, OpenERP, SMTP, IMAP, SQL, Amazon S3,
OpenStack Swift and more so it's guaranteed zato-apitest will grow support for more protocols and transport layers with time.

Here's a sample test case::

    Feature: Customer update

    Scenario: SOAP customer update

        Given address "http://example.com"
        Given URL path "/xml/customer"
        Given SOAP action "update:cust"
        Given HTTP method "POST"
        Given format "XML"
        Given namespace prefix "cust" of "http://example.com/cust"
        Given request "cust-update.xml"
        Given XPath "//cust:name" in request is "Maria"
        Given XPath "//cust:last-seen" in request is a random date before "2015-03-17" "default"

        When the URL is invoked

        Then XPath "//cust:action/cust:code" is an integer "0"
        And XPath "//cust:action/cust:msg" is "Ok, updated"

        And context is cleaned up

    Scenario: REST customer update

        Given address "http://example.com"
        Given URL path "/json/customer"
        Given query string "?id=123"
        Given HTTP method "PUT"
        Given format "JSON"
        Given header "X-Node" "server-test-19"
        Given request "cust-update.json"
        Given JSON Pointer "/name" in request is "Maria"
        Given JSON Pointer "/last-seen" in request is UTC now "default"

        When the URL is invoked

        Then JSON Pointer "/action/code" is an integer "0"
        And JSON Pointer "/action/message" is "Ok, updated"
        And status is "200"
        And header "X-My-Header" is "Cool"

More details, including plenty of usage examples, demos and screenshots, are `on GitHub <https://github.com/zatosource/zato-apitest>`_.
"""

def parse_requirements(requirements):
    ignored = ['#', 'setuptools', '-e']

    with open(requirements) as f:
        return [line for line in f if line.strip() and not any(line.startswith(prefix) for prefix in ignored)]

setup(
      name = 'zato-apitest',
      version = version,

      scripts = ['src/zato/apitest/console/apitest'],

      author = 'Dariusz Suchojad',
      author_email = 'dsuch at zato.io',
      url = 'https://github.com/zatosource/zato-apitest',
      description = 'API Testing for Humans',
      long_description = LONG_DESCRIPTION,
      platforms = ['OS Independent'],
      license = 'GNU Lesser General Public License v3 (LGPLv3)',

      package_dir = {'':b'src'},
      packages = find_packages(b'src'),

      namespace_packages = [b'zato'],
      install_requires = parse_requirements(
          os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')),

      zip_safe = False,

      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'Topic :: Education :: Testing',
        'Topic :: Internet',
        'Topic :: Internet :: Proxy Servers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
        ],
)
