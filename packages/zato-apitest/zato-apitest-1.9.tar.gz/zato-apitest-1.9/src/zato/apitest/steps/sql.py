# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Filip Kłosowski <filip at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Originally part of Zato - open-source ESB, SOA, REST, APIs and cloud integrations in Python
# https://zato.io

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import ast

# Behave
from behave import given, then

# sqlalchemy
from sqlalchemy import create_engine

# Zato
from .. import util

from .insert_csv import main as insert_csv

# ################################################################################################################################

@given('I connect to "{sqlalchemy_url}" as "{conn_name}"')
@util.obtain_values
def given_i_connect_to_sqlalchemy_url_as_conn_name(ctx, sqlalchemy_url, conn_name):
    engine = create_engine(sqlalchemy_url)
    connection = engine.connect()
    ctx.zato.user_ctx[conn_name] = connection

@given('I store "{sql}" query result under "{name}", using "{conn_name}"')
@util.obtain_values
def given_i_store_sql_query_result_under_name(ctx, sql, name, conn_name):
    conn = conn_name.execute(sql)
    result = conn.fetchall()
    if len(result) == 1:
        ctx.zato.user_ctx[name] = result[0][0]
    else:
        ctx.zato.user_ctx[name] = result

@then('SQL "{sql}" is equal to "{value}", using "{conn_name}"')
@util.obtain_values
def then_sql_is_equal_to_value_using_conn_name(ctx, sql, value, conn_name):
    conn = conn_name.execute(sql)
    actual = conn.fetchall()
    expected_value = ast.literal_eval(value)
    assert actual == expected_value, 'Value `{}` is not equal to expected `{}`'.format(actual, expected_value)

@then('I disconnect from SQL "{conn_name}"')
@util.obtain_values
def then_i_disconnect_from_sql(ctx, conn_name):
    conn_name.close()

# ###############################################################################################################################

@given('I store filter "{colname}" is "{sign}" "{colvalue}" "{operator}" under "{name}"')
def i_store_filter_under_name(ctx, colname, sign, colvalue, name, operator=None):
    criterion = util.build_filter(colname, sign, colvalue, operator)
    ctx.zato.user_ctx[name] = criterion

@then('I insert "{values}" into "{columns}" of SQL table "{tablename}", using "{conn_name}"')
@util.obtain_values
def then_i_insert_values_into_columns(ctx, tablename, values, columns, conn_name):

    if len(columns.split(', ')) != len(values.split(', ')):
        raise ValueError("Error: invalid number of column names and values.")

    insert = "INSERT INTO %s (%s) VALUES (%s)" % (tablename, columns, util.wrap_into_quotes(values))
    conn_name.execute(insert)
    return insert

@then('I update "{columns}" of SQL table "{tablename}" set "{values}" filter by "{criterion}", using "{conn_name}"')
@util.obtain_values
def then_i_update_columns_setting_values(ctx, tablename, columns, values, conn_name, criterion=None):
    if not criterion:
        criterion = ''
    column_value = util.make_dict(columns, values)
    for key in column_value.keys():
        insert = "UPDATE %s SET %s='%s' %s" %(tablename, key, column_value[key][0], criterion)
        conn_name.execute(insert)
    return insert

@then('I delete from SQL table "{tablename}" where "{criterion}", using "{conn_name}"')
@util.obtain_values
def then_i_delete_from_table(ctx, tablename, conn_name, criterion=None):
    if not criterion:
        criterion = ''
    insert = "DELETE FROM %s %s" %(tablename, criterion)
    conn_name.execute(insert)
    return insert

# this step's purpose is insertion of data from csv file to existing table;
# names of columns are taken from the header line of csv file
@then('I insert data from csv "{filename}" to SQL table "{tablename}", using "{conn_name}"')
@util.obtain_values
def i_insert_data_from_csv_file(ctx, **kwargs):
    insert_csv(use_header=1, **kwargs)

# this step's purpose is creation of a new table and insertion of data from csv file upon it;
# names of columns are automatically generated as col0, col1, col2 and so on
@then('I create SQL table "{tablename}" and insert data from csv "{filename}", using "{conn_name}"')
@util.obtain_values
def i_create_table_and_insert_data_from_csv(ctx, **kwargs):
    insert_csv(use_types='default', **kwargs)

# this step's purpose is creation of a new table and insertion of data from csv file upon it;
# data types and names of columns are taken from the header line of csv file
@then('I create SQL table "{tablename}" and insert data from csv "{filename}", \
using "{conn_name}" and names, data types from the header')
@util.obtain_values
def i_create_table_and_insert_data_from_csv_file_using_types_and_header(ctx, **kwargs):
    insert_csv(use_header=1, use_types=1, **kwargs)

# this step's purpose is creation of a new table and insertion of data from csv file upon it;
# names of columns are taken from the header line of csv file and data types are from dedicated line below the header
@then('I create SQL table "{tablename}" and insert data from csv "{filename}", using "{conn_name}", \
    names from the header and data types from the line below')
@util.obtain_values
def i_create_table_and_insert_data_from_csv_file_using_header(ctx, **kwargs):
    insert_csv(use_header=1, use_types=0, **kwargs)
