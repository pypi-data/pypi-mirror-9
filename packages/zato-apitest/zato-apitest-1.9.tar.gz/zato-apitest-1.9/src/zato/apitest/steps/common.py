# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Originally part of Zato - open-source ESB, SOA, REST, APIs and cloud integrations in Python
# https://zato.io

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import ast
import json
import time

# Behave
from behave import given, when, then

# Bunch
from bunch import Bunch

# datadiff
from datadiff.tools import assert_equals

# jsonpointer
from jsonpointer import resolve_pointer as get_pointer

# lxml
from lxml import etree

# Request
from requests import api as req_api
from requests.auth import HTTPBasicAuth

# Zato
from .. import util
from .. import AUTH, INVALID, NO_VALUE

# ################################################################################################################################

@when('the URL is invoked')
def when_the_url_is_invoked(ctx, adapters=None):
    adapters = adapters or []
    method = ctx.zato.request.get('method', 'GET')
    address = ctx.zato.request.get('address')
    url_path = ctx.zato.request.get('url_path', '/')
    qs = ctx.zato.request.get('query_string', '')

    if 'data_impl' in ctx.zato.request:
        if ctx.zato.request.is_xml:
            data = etree.tostring(ctx.zato.request.data_impl)
        elif ctx.zato.request.is_json:
            data = json.dumps(ctx.zato.request.data_impl, indent=2)
        elif ctx.zato.request.is_raw:
            data = ctx.zato.request.data_impl
    else:
        data = ''

    auth = None

    # New in 1.1 hence optional
    if ctx.zato.get('auth'):
        if ctx.zato.auth['type'] == AUTH.BASIC_AUTH:
            auth = HTTPBasicAuth(ctx.zato.auth['username'], ctx.zato.auth['password'])

    ctx.zato.response = Bunch()

    s = req_api.sessions.Session()
    for adapter in adapters:
        s.mount('http://', adapter)
        s.mount('https://', adapter)

    ctx.zato.response.data = s.request(
        method, '{}{}{}'.format(address, url_path, qs), data=data, headers=ctx.zato.request.headers, auth=auth)

    # if the reply format is unset, assume it's the same as the request format
    # if the request format hasn't been specified either, assume 'RAW"
    response_format = ctx.zato.request.get('response_format', ctx.zato.request.get('format', 'RAW'))

    if response_format == 'XML':
        ctx.zato.response.data_impl = etree.fromstring(ctx.zato.response.data.text.encode('utf-8'))

    elif response_format == 'JSON':
        ctx.zato.response.data_impl = json.loads(ctx.zato.response.data.text)

    elif response_format == 'RAW':
        ctx.zato.response.data_impl = ctx.zato.response.data.text

# ################################################################################################################################

@given('address "{address}"')
@util.obtain_values
def given_address(ctx, address):
    ctx.zato.request.address = address

@given('URL path "{url_path}"')
@util.obtain_values
def given_url_path(ctx, url_path):
    ctx.zato.request.url_path = url_path

@given('HTTP method "{method}"')
def given_http_method(ctx, method):
    ctx.zato.request.method = method

def set_request_format(ctx, format):
    ctx.zato.request.format = format

    ctx.zato.request.is_xml = ctx.zato.request.format == 'XML'
    ctx.zato.request.is_json = ctx.zato.request.format == 'JSON'
    ctx.zato.request.is_raw = ctx.zato.request.format == 'RAW'

@given('format "{format}"')
@util.obtain_values
def given_format(ctx, format):
    set_request_format(ctx, format)

@given('request format "{format}"')
@util.obtain_values
def given_request_format(ctx, format):
    set_request_format(ctx, format)

@given('response format "{format}"')
@util.obtain_values
def given_response_format(ctx, format):
    ctx.zato.request.response_format = format

@given('user agent is "{value}"')
@util.obtain_values
def given_user_agent_is(ctx, value):
    ctx.zato.request.headers['User-Agent'] = value

@given('header "{header}" "{value}"')
@util.obtain_values
def given_header(ctx, header, value):
    ctx.zato.request.headers[header] = value

def given_request_impl(ctx, data):

    ctx.zato.request.data = data

    if ctx.zato.request.get('is_xml'):
        ctx.zato.request.data_impl = etree.fromstring(ctx.zato.request.data)
    elif ctx.zato.request.get('is_json'):
        ctx.zato.request.data_impl = json.loads(ctx.zato.request.data)
    elif ctx.zato.request.get('is_raw'):
        ctx.zato.request.data_impl = ctx.zato.request.data
    else:
        if not ctx.zato.request.format:
            raise ValueError('Format not set, cannot proceed')

@given('request "{request_path}"')
@util.obtain_values
def given_request(ctx, request_path):
    return given_request_impl(ctx, util.get_data(ctx, 'request', request_path))

@given('request is "{data}"')
@util.obtain_values
def given_request_is(ctx, data):
    return given_request_impl(ctx, data)

@given('query string "{query_string}"')
@util.obtain_values
def given_query_string(ctx, query_string):
    ctx.zato.request.query_string = query_string

@given('date format "{name}" "{format}"')
@util.obtain_values
def given_date_format(ctx, name, format):
    ctx.zato.date_formats[name] = format

# ################################################################################################################################

@given('Basic Auth "{username}" "{password}"')
@util.obtain_values
def given_basic_auth(ctx, username, password):
    ctx.zato.auth['type'] = AUTH.BASIC_AUTH
    ctx.zato.auth['username'] = username
    ctx.zato.auth['password'] = password

# ################################################################################################################################

@given('I store "{value}" under "{name}"')
@util.obtain_values
def given_i_store_value_under_name(ctx, value, name):
    ctx.zato.user_ctx[name] = value

# ################################################################################################################################

@given('I store a random string under "{name}"')
@util.obtain_values
def given_i_store_a_random_string_under_name(ctx, name):
    ctx.zato.user_ctx[name] = util.rand_string()

# ################################################################################################################################

@given('I store a random integer under "{name}"')
@util.obtain_values
def given_i_store_a_random_integer_under_name(ctx, name):
    ctx.zato.user_ctx[name] = util.rand_int()

# ################################################################################################################################

@given('I store a random float under "{name}"')
@util.obtain_values
def given_i_store_a_random_float_under_name(ctx, name):
    ctx.zato.user_ctx[name] = util.rand_float()

# ################################################################################################################################

@given('I store a random date under "{name}", format "{format}"')
@util.obtain_values
def given_i_store_a_random_date_under_name(ctx, name, format):
    ctx.zato.user_ctx[name] = util.rand_date(ctx.zato.date_formats[format])

# ################################################################################################################################

@then('context is cleaned up')
@util.obtain_values
def then_context_is_cleaned_up(ctx):
    ctx.zato = util.new_context(ctx, None)

@then('status is "{expected_status}"')
@util.obtain_values
def then_status_is(ctx, expected_status):
    expected_status = int(expected_status)
    assert ctx.zato.response.data.status_code == expected_status, 'Status expected `{!r}`, received `{!r}`'.format(
        expected_status, ctx.zato.response.data.status_code)
    return True

@then('header "{expected_header}" is "{expected_value}"')
@util.obtain_values
def then_header_is(ctx, expected_header, expected_value):
    value = ctx.zato.response.data.headers[expected_header]
    assert value == expected_value, 'Expected for header `{}` to be `{}` instead of `{}`'.format(
        expected_header, expected_value, value)
    return True

@then('header "{expected_header}" isn\'t "{expected_value}"')
@util.obtain_values
def then_header_isnt(ctx, expected_header, expected_value):
    value = ctx.zato.response.data.headers[expected_header]
    assert expected_value != value, 'Expected for header `{}` not to be equal to `{}`'.format(
        expected_header, expected_value)
    return True

@then('header "{expected_header}" contains "{expected_value}"')
@util.obtain_values
def then_header_contains(ctx, expected_header, expected_value):
    value = ctx.zato.response.data.headers[expected_header]
    assert expected_value in value, 'Expected for header `{}` to contain `{}` in `{}`'.format(
        expected_header, expected_value, value)
    return True

@then('header "{expected_header}" doesn\'t contain "{expected_value}"')
@util.obtain_values
def then_header_doesnt_contain(ctx, expected_header, expected_value):
    value = ctx.zato.response.data.headers[expected_header]
    assert expected_value not in value, 'Header `{}` shouldn\'t contain `{}` in `{}`'.format(
        expected_header, expected_value, value)
    return True

@then('header "{expected_header}" exists')
@util.obtain_values
def then_header_exists(ctx, expected_header):
    value = ctx.zato.response.data.headers.get(expected_header, INVALID)
    assert value != INVALID, 'Header `{}` should be among `{}`'.format(expected_header, ctx.zato.response.data.headers)
    return True

@then('header "{expected_header}" doesn\'t exist')
@util.obtain_values
def then_header_doesnt_exist(ctx, expected_header):
    value = ctx.zato.response.data.headers.get(expected_header, INVALID)
    assert value == INVALID, 'Header `{}` shouldn\'t be among `{}`'.format(expected_header, ctx.zato.response.data.headers)
    return True

@then('header "{expected_header}" is empty')
@util.obtain_values
def then_header_is_empty(ctx, expected_header):
    value = ctx.zato.response.data.headers[expected_header]
    assert value == '', 'Header `{}` should be empty instead of `{}`'.format(expected_header, value)
    return True

@then('header "{expected_header}" isn\'t empty')
@util.obtain_values
def then_header_isnt_empty(ctx, expected_header):
    value = ctx.zato.response.data.headers[expected_header]
    assert value != '', 'Header `{}` shouldn\'t be empty'.format(expected_header)
    return True

@then('header "{expected_header}" starts with "{expected_value}"')
@util.obtain_values
def then_header_starts_with(ctx, expected_header, expected_value):
    value = ctx.zato.response.data.headers[expected_header]
    assert value.startswith(expected_value), 'Expected for header `{}` to start with `{}` but it\'s `{}`'.format(
        expected_header, expected_value, value)
    return True

@then('header "{expected_header}" doesn\'t start with "{expected_value}"')
@util.obtain_values
def then_header_doesnt_starts_with(ctx, expected_header, expected_value):
    value = ctx.zato.response.data.headers[expected_header]
    assert not value.startswith(expected_value), 'Expected for header `{}` not to start with `{}` yet it\'s `{}`'.format(
        expected_header, expected_value, value)
    return True

@then('header "{expected_header}" ends with "{expected_value}"')
@util.obtain_values
def then_header_ends_with(ctx, expected_header, expected_value):
    value = ctx.zato.response.data.headers[expected_header]
    assert value.endswith(expected_value), 'Expected for header `{}` to end with `{}` but it\'s `{}`'.format(
        expected_header, expected_value, value)
    return True

@then('header "{expected_header}" doesn\'t end with "{expected_value}"')
@util.obtain_values
def then_header_doesnt_end_with(ctx, expected_header, expected_value):
    value = ctx.zato.response.data.headers[expected_header]
    assert not value.endswith(expected_value), 'Expected for header `{}` not to end with `{}` yet it\'s `{}`'.format(
        expected_header, expected_value, value)
    return True

# ################################################################################################################################

@then('I store "{path}" from response under "{name}", default "{default}"')
@util.obtain_values
def then_store_path_under_name_with_default(ctx, path, name, default):
    if ctx.zato.request.is_xml:
        value = ctx.zato.response.data_impl.xpath(path)
        if value:
            if len(value) == 1:
                value = value[0].text
            else:
                value = [elem.text for elem in value]
        else:
            if default == NO_VALUE:
                raise ValueError('No such path `{}`'.format(path))
            else:
                value = default
    else:
        value = get_pointer(ctx.zato.response.data_impl, path, default)
        if value == NO_VALUE:
            raise ValueError('No such path `{}`'.format(path))

    ctx.zato.user_ctx[name] = value

@then('I store "{path}" from response under "{name}"')
@util.obtain_values
def then_store_path_under_name(ctx, path, name):
    return then_store_path_under_name_with_default(ctx, path, name, NO_VALUE)

# ################################################################################################################################

def needs_json(func):
    def inner(ctx, **kwargs):
        if ctx.zato.request.get('response_format', ctx.zato.request.get('format', 'RAW')) != 'JSON':
            raise TypeError('This step works with JSON replies only.')
        return func(ctx, **kwargs)
    return inner

def json_response_is_equal_to(ctx, expected):
    assert_equals(expected, ctx.zato.response.data_impl)
    return True

@then('response is equal to that from "{path}"')
@needs_json
@util.obtain_values
def then_response_is_equal_to_that_from(ctx, path):
    return json_response_is_equal_to(ctx, json.loads(util.get_data(ctx, 'response', path)))

@then('response is equal to "{expected}"')
@needs_json
@util.obtain_values
def then_response_is_equal_to(ctx, expected):
    return json_response_is_equal_to(ctx, json.loads(expected))

# ################################################################################################################################

@then('I sleep for "{sleep_time}"')
@util.obtain_values
def then_i_sleep_for(ctx, sleep_time):
    time.sleep(float(sleep_time))
    
# ################################################################################################################################

@given('I encode "{value}" using Base64 under "{name}"')
@util.obtain_values
def given_i_encode_value_using_base64_under_name(ctx, value, name):
    ctx.zato.user_ctx[name] = value.encode('base64','strict')

# ################################################################################################################################

def variable_is(variable, value):
    expected_value = ast.literal_eval(value)
    assert variable == expected_value, 'Value `{}` is not equal to expected `{}`'.format(variable, expected_value)

@then('variable "{variable}" is a list "{value}"')
@util.obtain_values
def and_variable_is_a_list(ctx, variable, value):
    variable_is(variable, value)

@then('variable "{variable}" is an empty list')
@util.obtain_values
def and_variable_is_an_empty_list(ctx, variable):
    assert variable == [], 'Value `{}` is not an empty list'.format(variable)

@then('variable "{variable}" is an integer "{value}"')
@util.obtain_values
def and_variable_is_an_integer(ctx, variable, value):
    variable_is(variable, value)

@then('variable "{variable}" is a float "{value}"')
@util.obtain_values
def and_variable_is_a_float(ctx, variable, value):
    variable_is(variable, value)

@then('variable "{variable}" is a string "{value}"')
@util.obtain_values
def and_variable_is_a_string(ctx, variable, value):
    assert variable == value, 'Value `{}` is not equal to expected `{}`'.format(variable, value)

@then('variable "{variable}" is True')
@util.obtain_values
def and_variable_is_true(ctx, variable):
    variable_is(variable, 'True')

@then('variable "{variable}" is False')
@util.obtain_values
def and_variable_is_false(ctx, variable):
    variable_is(variable, 'False')
