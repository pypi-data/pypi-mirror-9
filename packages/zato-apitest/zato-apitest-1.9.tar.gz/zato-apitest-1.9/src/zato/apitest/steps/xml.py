# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Originally part of Zato - open-source ESB, SOA, REST, APIs and cloud integrations in Python
# https://zato.io

from __future__ import absolute_import, division, print_function, unicode_literals

# Behave
from behave import given, then

# lxml
from lxml import etree

# Zato
from .. import util

# ################################################################################################################################

@given('namespace prefix "{prefix}" of "{namespace}"')
@util.obtain_values
def given_namespace_prefix(ctx, prefix, namespace):
    ctx.zato.request.ns_map[prefix] = namespace

@given('SOAP action "{value}"')
@util.obtain_values
def given_soap_action(ctx, value):
    ctx.zato.request.headers['SOAPAction'] = value

# ################################################################################################################################

def handle_xpath(is_request):
    def handle_xpath_impl(func, **ignored):
        def inner(ctx, **kwargs):
            xpath = kwargs.pop('xpath', kwargs.pop('elem', None))

            data = ctx.zato.request.data if is_request else ctx.zato.response.data.text
            data_impl = ctx.zato.request.data_impl if is_request else ctx.zato.response.data_impl

            elem = data_impl.xpath(xpath, namespaces=ctx.zato.request.ns_map)
            if elem is None or (isinstance(elem, list) and not elem):
                raise ValueError('No `{}` path in `{}` with NS map `{}`'.format(xpath, data, ctx.zato.request.ns_map))

            if len(elem) > 1:
                raise ValueError(
                    'Path `{}` points to more than one element in `{}` with NS map`{}`'.format(
                        xpath, data, ctx.zato.request.ns_map))

            elem = elem[0]
            if 'value' in kwargs:
                kwargs['value'] = kwargs['value'].encode('utf-8')

            return func(ctx, elem, **kwargs)
        return inner
    return handle_xpath_impl

@given('XPath "{xpath}" in request is "{value}"')
@handle_xpath(True)
@util.obtain_values
def given_xpath_in_request_is(ctx, elem, value, **ignored):
    elem.text = value

@given('XPath "{xpath}" in request is a random string')
@handle_xpath(True)
@util.obtain_values
def given_xpath_set_to_rand_string(ctx, elem, **ignored):
    elem.text = util.rand_string()

@given('XPath "{xpath}" in request is a random integer')
@handle_xpath(True)
@util.obtain_values
def given_xpath_set_to_rand_int(ctx, elem, **ignored):
    elem.text = str(util.rand_int())

@given('XPath "{xpath}" in request is a random float')
@handle_xpath(True)
@util.obtain_values
def given_xpath_set_to_rand_float(ctx, elem, **ignored):
    elem.text = str(util.rand_float())

# ################################################################################################################################

@given('XPath "{xpath}" in request is a random date "{format}"')
@handle_xpath(True)
@util.obtain_values
def given_xpath_is_rand_date(ctx, elem, format, **ignored):
    elem.text = util.rand_date(ctx.zato.date_formats[format])

@given('XPath "{xpath}" in request is now "{format}"')
@handle_xpath(True)
@util.obtain_values
def given_xpath_is_now(ctx, elem, format, **ignored):
    elem.text = util.now(format=ctx.zato.date_formats[format])

@given('XPath "{xpath}" in request is UTC now "{format}"')
@handle_xpath(True)
@util.obtain_values
def given_xpath_is_utc_now(ctx, elem, format, **ignored):
    elem.text = util.utcnow(format=ctx.zato.date_formats[format])

@given('XPath "{xpath}" in request is a random date after "{date_start}" "{format}"')
@handle_xpath(True)
@util.obtain_values
def given_xpath_is_rand_date_after(ctx, elem, date_start, format, **ignored):
    elem.text = util.date_after(date_start, ctx.zato.date_formats[format])

@given('XPath "{xpath}" in request is a random date before "{date_end}" "{format}"')
@handle_xpath(True)
@util.obtain_values
def given_xpath_is_rand_date_before(ctx, elem, date_end, format, **ignored):
    elem.text = util.date_before(date_end, ctx.zato.date_formats[format])

@given('XPath "{xpath}" in request is a random date between "{date_start}" and "{date_end}" "{format}"')
@handle_xpath(True)
@util.obtain_values
def given_xpath_is_rand_date_between(ctx, elem, date_start, date_end, format, **ignored):
    elem.text = util.date_between(date_start, date_end, ctx.zato.date_formats[format])

# ################################################################################################################################

@given('XPath "{xpath}" in request is one of "{value}"')
@handle_xpath(True)
@util.obtain_values
def given_xpath_set_to_one_of(ctx, elem, value, **ignored):
    elem.text = util.any_from_list(value)

# ################################################################################################################################

def _assert_xpath_value(ctx, elem, force_type=None, **kwargs):
    elem_text = elem.text if elem.text is not None else ''
    value = expected_value = kwargs['value']

    if force_type:
        elem_text = force_type(elem_text)
        value = force_type(value)

    assert elem_text == value, '`{!r}` is `{!r}` instead of `{!r}` in `{!r}`'.format(
        elem, elem_text, expected_value, etree.tostring(elem))

@then('XPath "{elem}" is "{value}"')
@handle_xpath(False)
@util.obtain_values
def then_xpath_is(ctx, elem, **kwargs):
    return _assert_xpath_value(ctx, elem, force_type=None, **kwargs)

@then('XPath "{elem}" is an integer "{value}"')
@handle_xpath(False)
@util.obtain_values
def then_xpath_is_an_integer(ctx, elem, **kwargs):
    return _assert_xpath_value(ctx, elem, force_type=int, **kwargs)

@then('XPath "{elem}" is a float "{value}"')
@handle_xpath(False)
@util.obtain_values
def then_xpath_is_a_float(ctx, elem, **kwargs):
    return _assert_xpath_value(ctx, elem, force_type=float, **kwargs)

@then('XPath "{elem}" is empty')
@handle_xpath(False)
@util.obtain_values
def then_xpath_is_empty(ctx, elem, **kwargs):
    return _assert_xpath_value(ctx, elem, value='')

@then('XPath "{elem}" isn\'t empty')
@handle_xpath(False)
@util.obtain_values
def then_xpath_is_not_empty(ctx, elem, **kwargs):
    assert elem.text != '', 'Elem `{!r} should not be empty, value: `{}`'.format(elem, etree.tostring(elem))

@then('XPath "{elem}" is one of "{value}"')
@handle_xpath(False)
@util.obtain_values
def then_xpath_is_one_of(ctx, elem, value, **kwargs):
    value = util.parse_list(value)
    assert elem.text in value, 'Elem `{!r} should be among `{}`'.format(etree.tostring(elem), value)

@then('XPath "{elem}" isn\'t one of "{value}"')
@handle_xpath(False)
@util.obtain_values
def then_xpath_is_not_one_of(ctx, elem, value, **kwargs):
    value = util.parse_list(value)
    assert elem.text not in value, 'Elem `{!r} should not be among `{}`'.format(etree.tostring(elem), value)
