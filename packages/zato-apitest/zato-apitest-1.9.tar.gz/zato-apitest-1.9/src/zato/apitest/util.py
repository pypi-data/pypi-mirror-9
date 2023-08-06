# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Originally part of Zato - open-source ESB, SOA, REST, APIs and cloud integrations in Python
# https://zato.io

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import csv, operator, os, random, uuid
from collections import OrderedDict
from datetime import timedelta
from itertools import izip_longest

# Arrow
from arrow import api as arrow_api

# Bunch
from bunch import Bunch, bunchify

# ConfigObj
from configobj import ConfigObj

# Dateutil
from dateutil.parser import parse as parse_dt

# six
from six.moves import cStringIO as StringIO

# Zato
from zato.apitest import version

random.seed()

# Singleton used for storing Zato's own context across features and steps.
# Not thread/greenlet-safe so this will have to be added if need be.
context = Bunch()

# ################################################################################################################################

def get_value_from_environ(ctx, name):
    return os.environ[name]

def get_value_from_ctx(ctx, name):
    return ctx.zato.user_ctx[name]

def get_value_from_config(ctx, name):
    return ctx.zato.user_config[name]

config_functions = {
    '$': get_value_from_environ,
    '#': get_value_from_ctx,
    '@': get_value_from_config
}

def obtain_values(func):
    """ Functions decorated with this one will be able to obtain values from config sources prefixed with $, # or @.
    """
    def inner(ctx, *args, **kwargs):
        for kwarg, value in kwargs.items():
            if value:
                config_key = value[0]
                if config_key in config_functions:
                    config_func = config_functions[config_key]
                    kwargs[kwarg] = config_func(ctx, value[1:])
        return func(ctx, *args, **kwargs)
    return inner

# ################################################################################################################################

def new_context(old_ctx, environment_dir, user_config=None):
    _context = Bunch()
    _context.auth = {}
    _context.user_ctx = {}
    _context.date_formats = {'default':'YYYY-MM-DDTHH:mm:ss'}
    _context.environment_dir = old_ctx.zato.environment_dir if old_ctx else environment_dir
    _context.request = Bunch()
    _context.request.headers = {'User-Agent':'zato-apitest/{} (+https://zato.io)'.format(version)}
    _context.request.ns_map = {}
    _context.user_config = user_config if user_config is not None else bunchify(
        ConfigObj(os.path.join(_context.environment_dir, 'config.ini')))['user']
    _context.cassandra_ctx = {}

    context.clear()
    context.update(_context)

    return context

# ################################################################################################################################

def get_full_path(base_dir, *path_items):
    return os.path.normpath(os.path.join(base_dir, *path_items))

def get_file(path):
    return open(path).read()

def get_data(ctx, req_or_resp, data_path):

    full_path = get_full_path(ctx.zato.environment_dir,
                              ctx.zato.request.get('response_format', ctx.zato.request.get('format', 'RAW')).lower(),
                              req_or_resp,
                              data_path)

    data = get_file(full_path) if data_path else ''

    if ctx.zato.request.format == 'XML' and not data:
        raise ValueError('No {} in `{}`'.format(req_or_resp, data_path))

    return data

# ################################################################################################################################

def parse_list(value):
    return tuple(csv.reader(StringIO(value)))[0]

def any_from_list(value):
    return random.choice(tuple(elem.strip() for elem in parse_list(value) if elem)).decode('utf-8')

# ################################################################################################################################

def rand_string(count=1):
    # First character is 'a' so it nevers starts with a digit.
    # Some parsers will insist a string is an integer if they notice a digit at idx 0.
    if count == 1:
        return 'a' + uuid.uuid4().hex
    else:
        return ['a' + uuid.uuid4().hex for x in range(count)]

def rand_int(min=0, max=100, count=1):
    if count == 1:
        return random.choice(range(min, max))
    else:
        return [random.choice(range(min, max)) for x in range(count)]

def rand_float(min=0, max=100):
    return float(rand_int(min, max)) + random.random()

def rand_date(format, start=None, stop=None):
    if not(start and stop):
        # Now is as random as any other date
        return now(format)

# ################################################################################################################################

def now(format):
    return arrow_api.now().format(format)

def utcnow(format):
    return arrow_api.utcnow().format(format)

# ################################################################################################################################

def date_after_before(base_date, format, direction, limit, needs_parse=True):
    if needs_parse:
        base_date = parse_dt(base_date)

    days=rand_int(0, abs(limit))
    return arrow_api.get(direction(base_date, timedelta(days=days))).format(format)

def date_after(base_date, format, limit=100000, needs_parse=True):
    return date_after_before(base_date, format, operator.add, limit, needs_parse)

def date_before(base_date, format, limit=100000, needs_parse=True):
    return date_after_before(base_date, format, operator.sub, limit, needs_parse)

def date_between(start_date, end_date, format):
    start_date = parse_dt(start_date)
    end_date = parse_dt(end_date)

    diff = int((start_date - end_date).days)
    func = date_after if end_date > start_date else date_before
    return func(start_date, format, diff, False)

# ################################################################################################################################

comparison_operators = {'equal to': '=',
                        'not equal to': '!=',
                        'less than': '<',
                        'greater than': '>',
                        'less or equal to': '<=',
                        'greater or equal to': '>='}
                                    
def wrap_into_quotes(values):
    return '\'{}\''.format('\', \''.join(values.split(', ')))

def make_dict(*args):
    components = []
    phrases = OrderedDict()
    for item in args:
        components.append([segment.strip() for segment in item.split(',')])
    for items in izip_longest(*components):
        phrases[items[0]] = items[1:]
    return phrases

def build_filter(*args):
    filter_dict = make_dict(*args)
    filter_ = ''
    for i, key in enumerate(filter_dict.keys()):
        operator = comparison_operators[filter_dict[key][0]]
        if filter_dict[key][2] is not None:
            join_by = filter_dict[key][2]
        if i == 0:
            filter_ += "WHERE %s%s'%s' " % (key, operator, filter_dict[key][1])
        else:
            filter_ += "%s %s%s'%s' " % (join_by, key, operator, filter_dict[key][1])
    return filter_
