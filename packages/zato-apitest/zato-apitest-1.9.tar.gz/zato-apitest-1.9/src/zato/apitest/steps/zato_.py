# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Filip Kłosowski <filip at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Originally part of Zato - open-source ESB, SOA, REST, APIs and cloud integrations in Python
# https://zato.io

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from httplib import OK
import json
from os.path import split

# requests
import requests

# Behave
from behave import given, when

# Zato
from .. import util

# ###############################################################################################################################

@given('I store "{cluster_id}" "{url_path}" "{username}" "{password}" under Zato "{conn_name}"')
@util.obtain_values
def given_i_store_zato_info_under_conn_name(ctx, cluster_id, url_path, username, password, conn_name):
    ctx.zato.user_ctx[conn_name] = {
        'cluster_id': cluster_id,
        'url_path': url_path,
        'username': username,
        'password': password
    }

@when('I upload a Zato service from "{module_path}" to "{conn_name}"')
@util.obtain_values
def when_i_upload_a_zato_service_from_path_to_conn_details(ctx, module_path, conn_name):
    with open(module_path, 'r') as module:
        service_code = module.read().encode('base64', 'strict')
        payload = json.dumps({
            'cluster_id': conn_name['cluster_id'],'payload': service_code,
            'payload_name': split(module_path)[-1]
            }, ensure_ascii=False)

        response = requests.get(conn_name['url_path'], auth=(conn_name['username'], conn_name['password']), data=payload)
        assert response.status_code == OK
