# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Filip Klosowski <filip at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import csv, os, re
from datetime import date, datetime
from itertools import izip
from time import strptime

# ################################################################################################################################

def str2date(s):
    s = s.replace('?', '1')
    return date(*strptime(s, "%Y-%m-%d")[0:3])

def str2datetime(s):
    return datetime(*strptime(s, "%Y-%m-%dT%H:%M:%S")[0:6])

def str2uni(s):
    return s.decode('utf-8')

type_convert = {'integer': int,
               'float': float,
               'numeric': float,
               'decimal': float,
               'text': str2uni,
               'char': str2uni,
               'varchar': str2uni,
               'date': str2date,
               'datetime': str2datetime}

class CSVFile(object):
    def __init__(self, filename, ctx=None, strip=True):

        if ctx and not os.path.isabs(filename):
            filename = os.path.join(ctx.zato.environment_dir, filename)

        sniffer = csv.Sniffer() # sniff delimiter 
        sample = open(filename, 'rb')
        dialect = sniffer.sniff(sample.readline())
        sample.seek(0)

        self.reader = csv.reader(open(filename, 'rb'),
                                 delimiter=dialect.delimiter,
                                 skipinitialspace=1)
        self.strip = strip
        self.cached_rows = []
        self.index = 0

    def __iter__(self):
        return self

    def readrow(self):
        row = None
        while not row:
            row = self.reader.next()
        return [x.strip() for x in row]

    def next(self):
        if self.cached_rows is None:
            return self.readrow()
        else:
            try:
                newrow = self.cached_rows[self.index]
            except IndexError:
                newrow = self.readrow()
                self.cached_rows.append(newrow)
            self.index += 1
        return newrow

    def rewind(self, index):
        self.index = index

    def getindex(self):
        return self.index


def parse_columns(csvf, flag=None):
    if flag:
        cols = [re.findall(r"\w+",item)[0] for item in csvf.next()]
    else:
        colrow = csvf.next()
        cols = ['col%d' % x for x in xrange(len(colrow))]
    return cols

def parse_types(csv, opt=None):
    types = []
    if opt == 0:
        # data types in dedicated line below the header line
        for t in csv.next():
            items = re.findall(r'\w+', t)
            types.append(tuple((element) for element in items[opt:]))
    if opt == 1:
        csv.rewind(0)
        # data types beside column names,
        # values are delimited by non alphanumerich character, like:
        # id:integer, name-varchar-30, income/float/5
        for t in csv.next():
            items = re.findall(r'\w+', t)
            types.append(tuple((element) for element in items[opt:]))
    if opt == 'default':
        csv.rewind(0)
        for item in csv.next():
            types.append(('text',))
        csv.rewind(0)
    return types

def prepare_table(conn_name, name, coltypes):
    declare_columns = []
    for col, col_type in coltypes:
        size = None
        if len(col_type) < 2:
            col_type = col_type[0]
        else:
            col_type, size = col_type
        if size:
            col_type = '%s(%s)' % (col_type, size)

        declare_columns.append('"%s" %s' % (col, col_type))

    return 'CREATE TABLE %s (\n%s\n);' % (name, ',\n'.join(declare_columns))

def create_table(conn_name, table_statement):
    conn_name.execute(table_statement)

def insert_from_csv(conn_name, csv, table, cols, types=None):
    len_cols = len(cols)
    insert_stmt = """INSERT INTO %s (%s) VALUES (%s)""" % (table, ','.join('"%s"' % x for x in cols), ','.join(['%s'] * len_cols))

    def get_conversion(t):
        if isinstance(t, tuple):
            t = t[0]
        return type_convert[t]

    def wrap_into_quotes(values):
        return '\'{}\''.format(values)

    if types is not None:
        converters = map(get_conversion, types)
        for row in csv:
            values = [conv(val) for conv, val in izip(converters, row)]
            values.extend([None] * (len_cols - len(values)))
            insert = insert_stmt % (tuple((wrap_into_quotes(element)) for element in values))
            conn_name.execute(insert)
    else:
        for row in csv:
            values = [val for val in row]
            values.extend([None] * (len_cols - len(values)))
            insert = insert_stmt % (tuple((wrap_into_quotes(element)) for element in values))
            conn_name.execute(insert)

def main(filename, tablename, conn_name, use_header=None, use_types=None):
    csvf = CSVFile(filename)
    cols = parse_columns(csvf, use_header)
    if use_types is not None:

        # use_types=default: all columns data type is 'text'
        # use_types=0: data types in dedicated line below the header line
        # use_types=1: data types beside column names

        types = parse_types(csvf, use_types)
        if len(cols) != len(types):
            raise ValueError("Error: invalid number of column names and types.")

        coltypes = zip(cols, types)
        table_statement = prepare_table(conn_name, tablename, coltypes)
        create_table(conn_name, table_statement)
        insert_from_csv(conn_name, csvf, tablename, cols, types)
    else:
        insert_from_csv(conn_name, csvf, tablename, cols)
