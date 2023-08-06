# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Filip Kłosowski <filip at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import ast
from collections import OrderedDict

# Behave
from behave import given, then

# Cassandra
from cassandra.cluster import Cluster

# Zato
from .. import util

from .insert_csv import CSVFile

# ################################################################################################################################

class TypeConverter(object):
    def __init__(self, csv_string):
        self.lists_dict = None
        self.text = None
        self.csv_string = csv_string
        self.altered_csv_string = self.parse_lists(self.csv_string)
        self.types = self.data_converter(self.altered_csv_string, self.lists_dict)

    def tryeval(self, string):
        try:
            data = ast.literal_eval(string)
        except:
            data = '\'{}\''.format(string)
        return data

    def find_substring_indices(self, string, sub):
        listindex=[]
        offset=0
        i = string.find(sub, offset)

        while i >= 0:
            listindex.append(i)
            i = string.find(sub, i + 1)
        return listindex

    def replace_all(self, text, dic):
        for k, v in dic.iteritems():
            text = text.replace(v, k)
        return text

    def parse_lists(self, string):
        self.lists_dict = OrderedDict()
        start = self.find_substring_indices(string, '[')
        end = self.find_substring_indices(string, ']')
        indices = [(x, y) for x, y in zip(start, end)]
        for idx, item in enumerate(indices):
            self.lists_dict['~' + str(idx)] = str(string[item[0]:item[1] + 1])
        self.text = self.replace_all(string, self.lists_dict)
        return self.text

    def data_converter(self, csv_string, dic):
        types = []
        for item in csv_string.split(','):
            if not item.strip().startswith('~'):
                val = self.tryeval((item.strip()).rstrip())
                types.append(val)
            else:
                s = (item.strip()).rstrip()
                val = self.tryeval(dic[s])
                types.append(val)
        return types

@given('Cassandra contact points "{contact_points}"')
@util.obtain_values
def given_cassandra_contact_points(ctx, contact_points):
    ctx.zato.cassandra_ctx['contact_points'] = [point.strip() for point in contact_points.split(',')]

@given('Cassandra protocol version "{protocol_version}"')
@util.obtain_values
def given_cassandra_protocol_version(ctx, protocol_version):
    ctx.zato.cassandra_ctx['protocol_version'] = int(protocol_version)

@given('Cassandra port "{port}"')
@util.obtain_values
def given_cassandra_port(ctx, port):
    ctx.zato.cassandra_ctx['port'] = int(port)

@given('I connect to keyspace "{keyspace}" as "{conn_name}"')
@util.obtain_values
def given_i_connect_to_keyspace_as_session(ctx, keyspace, conn_name):
    if len(ctx.zato.cassandra_ctx) > 0:
        cluster = Cluster(**ctx.zato.cassandra_ctx)
    else:
        cluster = Cluster()
    session = cluster.connect(keyspace)
    ctx.zato.user_ctx[conn_name] = session

@given('I store CQL query result "{cql}" under "{name}", using "{conn_name}", idx "{idx}"')
@util.obtain_values
def given_i_store_cql_query_result_under_name(ctx, cql, name, conn_name, idx):

    values = []
    result = ctx.zato.user_ctx[conn_name].execute(cql)

    if result:
        result = result[int(idx)]
        result = result._asdict()

        for k, v in result.items():
            values.append(v)

    ctx.zato.user_ctx[name] = ';'.join(values)

@given('I insert data from CSV "{filename}" to Cassandra table "{tablename}", using "{conn_name}"')
@util.obtain_values
def i_insert_data_from_csv_file_to_cassandra_table(ctx, filename, tablename, conn_name):
    csvf = CSVFile(filename, ctx)
    colnames = [item for item in csvf.next()]
    statement = "INSERT INTO %s (%s) VALUES (%s)"
    for row in csvf:
        value_types = TypeConverter(','.join(row)).types
        data = (tablename, ','.join('%s' % (s.strip()).rstrip() for s in colnames), ','.join('%s' % v for v in value_types))
        insert = statement % data
        ctx.zato.user_ctx[conn_name].execute(insert)

# ###############################################################################################################################

@then('I disconnect from Cassandra "{conn_name}"')
@util.obtain_values
def then_i_disconnect_from_cassandra(ctx, conn_name):
    ctx.zato.user_ctx[conn_name].shutdown()

@then('I insert "{values}" into "{columns}" of Cassandra table "{tablename}", using "{conn_name}"')
@util.obtain_values
def then_i_insert_values_into_columns_of_cassandra_table(ctx, tablename, values, columns, conn_name):
    cols = columns.split(',')

    if len(cols) != len(values.split(',')):
        raise ValueError("Error: invalid number of column names and values.")

    value_types = TypeConverter(values).types
    insert = "INSERT INTO %s (%s) VALUES (%s)" % (
        tablename, ','.join('%s' % (x.strip()).rstrip() for x in cols), ','.join('%s' % x for x in value_types))
    ctx.zato.user_ctx[conn_name].execute(insert)

@then('I update "{columns}" of Cassandra table "{tablename}" set "{values}" filter by "{criterion}", using "{conn_name}"')
@util.obtain_values
def then_i_update_columns_of_cassandra_table_setting_values(ctx, tablename, columns, values, conn_name, criterion):
    column_value = util.make_dict(columns, values)
    for key in column_value.keys():
        insert = "UPDATE %s SET %s='%s' %s" % (tablename, key, column_value[key][0], criterion)
        ctx.zato.user_ctx[conn_name].execute(insert)

@then('I delete from Cassandra table "{tablename}" where "{criterion}", using "{conn_name}"')
@util.obtain_values
def then_i_delete_from_cassandra_table(ctx, tablename, conn_name, criterion=None):
    if not criterion:
        criterion = ''
    insert = "DELETE FROM %s %s" % (tablename, criterion)
    ctx.zato.user_ctx[conn_name].execute(insert)
