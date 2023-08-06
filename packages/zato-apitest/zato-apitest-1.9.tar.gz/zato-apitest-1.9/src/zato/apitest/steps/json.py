# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Originally part of Zato - open-source ESB, SOA, REST, APIs and cloud integrations in Python
# https://zato.io

from __future__ import absolute_import, division, print_function, unicode_literals

# base32_crockford
from base32_crockford import decode as crockford_decode

# Behave
from behave import given, then

# datadiff
from datadiff.tools import assert_equals

# jsonpointer
from jsonpointer import resolve_pointer as get_pointer, set_pointer as _set_pointer

# Zato
from .. import util
from .. import INVALID

# Integer types for testing 'JSON Pointer {path} is any integer'
try:
    int_types = (int, long)
except:
    int_types = (int,)     # python 3 doesn't have the long type


# ################################################################################################################################

def set_pointer(ctx, path, value):
    if 'data_impl' not in ctx.zato.request:
        raise ValueError('JSON Pointer called but no request set')

    _set_pointer(ctx.zato.request.data_impl, path, value)

# ################################################################################################################################

@given('JSON Pointer "{path}" in request is "{value}"')
@util.obtain_values
def given_json_pointer_in_request_is(ctx, path, value):
    set_pointer(ctx, path, value)

@given('JSON Pointer "{path}" in request is an integer "{value}"')
@util.obtain_values
def given_json_pointer_in_request_is_an_integer(ctx, path, value):
    set_pointer(ctx, path, int(value))

@given('JSON Pointer "{path}" in request is a float "{value}"')
@util.obtain_values
def given_json_pointer_in_request_is_a_float(ctx, path, value):
    set_pointer(ctx, path, float(value))

@given('JSON Pointer "{path}" in request is a list "{value}"')
@util.obtain_values
def given_json_pointer_in_request_is_a_list(ctx, path, value):
    set_pointer(ctx, path, util.parse_list(value))

@given('JSON Pointer "{path}" in request is a random string')
@util.obtain_values
def given_json_pointer_in_request_is_a_random_string(ctx, path):
    set_pointer(ctx, path, util.rand_string())

@given('JSON Pointer "{path}" in request is a random integer')
@util.obtain_values
def given_json_pointer_in_request_is_a_random_integer(ctx, path):
    set_pointer(ctx, path, util.rand_int())

@given('JSON Pointer "{path}" in request is a random float')
@util.obtain_values
def given_json_pointer_in_request_is_a_random_float(ctx, path):
    set_pointer(ctx, path, util.rand_float())

@given('JSON Pointer "{path}" in request is one of "{value}"')
@util.obtain_values
def given_json_pointer_in_request_is_one_of(ctx, path, value):
    set_pointer(ctx, path, util.any_from_list(value))

# ################################################################################################################################

@given('JSON Pointer "{path}" in request is a random date "{format}"')
@util.obtain_values
def given_json_pointer_is_rand_date(ctx, path, format):
    set_pointer(ctx, path, util.rand_date(ctx.zato.date_formats[format]))

@given('JSON Pointer "{path}" in request is now "{format}"')
@util.obtain_values
def given_json_pointer_is_now(ctx, path, format):
    set_pointer(ctx, path, util.now(format=ctx.zato.date_formats[format]))

@given('JSON Pointer "{path}" in request is UTC now "{format}"')
@util.obtain_values
def given_json_pointer_is_utc_now(ctx, path, format):
    set_pointer(ctx, path, util.utcnow(format=ctx.zato.date_formats[format]))

@given('JSON Pointer "{path}" in request is a random date after "{date_start}" "{format}"')
@util.obtain_values
def given_json_pointer_is_rand_date_after(ctx, path, date_start, format):
    set_pointer(ctx, path, util.date_after(date_start, ctx.zato.date_formats[format]))

@given('JSON Pointer "{path}" in request is a random date before "{date_end}" "{format}"')
@util.obtain_values
def given_json_pointer_is_rand_date_before(ctx, path, date_end, format):
    set_pointer(ctx, path, util.date_before(date_end, ctx.zato.date_formats[format]))

@given('JSON Pointer "{path}" in request is a random date between "{date_start}" and "{date_end}" "{format}"')
@util.obtain_values
def given_json_pointer_is_rand_date_between(ctx, path, date_start, date_end, format):
    set_pointer(ctx, path, util.date_between(date_start, date_end, ctx.zato.date_formats[format]))

# ################################################################################################################################

def assert_value(ctx, path, value, wrapper=None):
    if 'data_impl' not in ctx.zato.response:
        raise ValueError('Assertion called but no format set')

    value = wrapper(value) if wrapper else value
    actual = get_pointer(ctx.zato.response.data_impl, path)
    assert_equals(value, actual)
    return True

@then('JSON Pointer "{path}" is "{value}"')
@util.obtain_values
def then_json_pointer_is(ctx, path, value):
    return assert_value(ctx, path, value)

@then('JSON Pointer "{path}" is an integer "{value}"')
@util.obtain_values
def then_json_pointer_is_an_integer(ctx, path, value):
    return assert_value(ctx, path, value, int)

@then('JSON Pointer "{path}" is any integer')
@util.obtain_values
def then_json_pointer_is_any_integer(ctx, path):
    actual = get_pointer(ctx.zato.response.data_impl, path)
    assert isinstance(actual, int_types), \
        'Expected an integer in {}, got a `{}`'.format(path, type(actual))
    return True

@then('JSON Pointer "{path}" is a float "{value}"')
@util.obtain_values
def then_json_pointer_is_a_float(ctx, path, value):
    return assert_value(ctx, path, value, float)

@then('JSON Pointer "{path}" is any float')
@util.obtain_values
def then_json_pointer_is_any_float(ctx, path):
    actual = get_pointer(ctx.zato.response.data_impl, path)
    assert isinstance(actual, float), \
        'Expected a float in {}, got a `{}`'.format(path, type(actual))
    return True

@then('JSON Pointer "{path}" is a list "{value}"')
@util.obtain_values
def then_json_pointer_is_a_list(ctx, path, value):
    return assert_value(ctx, path, value, util.parse_list)

@then('JSON Pointer "{path}" is empty')
@util.obtain_values
def then_json_pointer_is_empty(ctx, path):
    return assert_value(ctx, path, '')

@then('JSON Pointer "{path}" isn\'t empty')
@util.obtain_values
def then_json_pointer_isnt_empty(ctx, path):
    actual = get_pointer(ctx.zato.response.data_impl, path, INVALID)
    assert actual != INVALID, 'Path `{}` Should not be empty'.format(path)

@then('JSON Pointer "{path}" is one of "{value}"')
@util.obtain_values
def then_json_pointer_is_one_of(ctx, path, value):
    actual = get_pointer(ctx.zato.response.data_impl, path)
    value = util.parse_list(value)
    assert actual in value, 'Expected for `{}` ({}) to be in `{}`'.format(actual, path, value)

@then('JSON Pointer "{path}" isn\'t one of "{value}"')
@util.obtain_values
def then_json_pointer_isnt_one_of(ctx, path, value):
    actual = get_pointer(ctx.zato.response.data_impl, path)
    value = util.parse_list(value)
    assert actual not in value, 'Expected for `{}` ({}) not to be in `{}`'.format(actual, path, value)

@then('JSON Pointer "{path}" is a BASE32 Crockford, checksum "{checksum}"')
@util.obtain_values
def then_json_pointer_is_a_base32_crockford(ctx, path, checksum):
    actual = get_pointer(ctx.zato.response.data_impl, path)
    crockford_decode(actual.replace('-', ''), checksum.lower() == 'true')

# ###############################################################################################################################

@then('JSON Pointer "{path}" is True')
@util.obtain_values
def then_json_pointer_is_true(ctx, path):
    return assert_value(ctx, path, True)

@then('JSON Pointer "{path}" is False')
@util.obtain_values
def then_json_pointer_is_false(ctx, path):
    return assert_value(ctx, path, False)

@then('JSON Pointer "{path}" is an empty list')
@util.obtain_values
def then_json_pointer_is_an_empty_list(ctx, path):
    return assert_value(ctx, path, [])

@then('JSON Pointer "{path}" is an empty dict')
@util.obtain_values
def then_json_pointer_is_an_empty_dict(ctx, path):
    return assert_value(ctx, path, {})

@then('JSON Pointer "{path}" isn\'t a string "{value}"')
@util.obtain_values
def then_json_pointer_isnt_a_string(ctx, path, value):
    actual = get_pointer(ctx.zato.response.data_impl, path)
    assert actual != value, 'Expected `{}` != `{}`'.format(actual, value)
