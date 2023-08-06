import argparse
import csv
import locale
import logging
import os
import sys
import types


def sql_print_table_mysql(columns, tablename):
    print 'DROP TABLE IF EXISTS tmp_' + tablename + ';'
    print 'CREATE TABLE tmp_' + tablename + ' ('
    i = 0
    for c in columns:
        column_type = 'VARCHAR'
        if c.type == types.FloatType:
            column_type = 'DOUBLE'
        elif c.type == types.StringType:
            if c.max_length == 1:
                column_type = 'CHAR(' + str(c.max_length) + ')'
            elif (c.max_length - c.min_length) <= 1:
                column_type = 'CHAR(' + str(c.max_length) + ')'
            else:
                column_type = 'VARCHAR(' + str(c.max_length) + ')'
        else:
            column_type = 'INT DEFAULT NULL'

        i = i + 1
        if i != len(columns):
            print '    ' + str(c.name) + ' ' + column_type + ','
        else:
            print '    ' + str(c.name) + ' ' + column_type
    print ');'

    print 'DROP TABLE IF EXISTS ' + tablename + ';'
    print 'CREATE TABLE ' + tablename + ' ('
    print '    _' + tablename + '_id INT(10) unsigned NOT NULL AUTO_INCREMENT,'
    for c in columns:
        column_type = 'VARCHAR'
        if c.type == types.FloatType:
            column_type = 'DOUBLE'
        elif c.type == types.StringType:
            if c.max_length == 1:
                column_type = 'CHAR(' + str(c.max_length) + ')'
            elif (c.max_length - c.min_length) <= 1:
                column_type = 'CHAR(' + str(c.max_length) + ')'
            else:
                column_type = 'VARCHAR(' + str(c.max_length) + ')'
        else:
            column_type = 'INT'

        print '    ' + str(c.name) + ' ' + column_type + ','
    print '    PRIMARY KEY (_' + tablename + '_id)'
    print ');'


def sql_print_table_sqlite(columns, tablename):
    print 'DROP TABLE IF EXISTS tmp_' + tablename + ';'
    print 'CREATE TABLE tmp_' + tablename + ' ('
    i = 0
    for c in columns:
        column_type = 'TEXT'
        if c.type == types.FloatType:
            column_type = 'REAL'
        elif c.type == types.StringType:
            column_type = 'TEXT'
        else:
            column_type = 'INTEGER'


        i = i + 1
        if i != len(columns):
            print '    ' + str(c.name) + ' ' + column_type + ','
        else:
            print '    ' + str(c.name) + ' ' + column_type
    print ');'


    print 'DROP TABLE IF EXISTS ' + tablename + ';'
    print 'CREATE TABLE ' + tablename + ' ('
    print '    _' + tablename + '_id INTEGER PRIMARY KEY AUTOINCREMENT,'
    i = 0
    for c in columns:
        column_type = 'TEXT'
        if c.type == types.FloatType:
            column_type = 'REAL'
        elif c.type == types.StringType:
            column_type = 'TEXT'
        else:
            column_type = 'INTEGER'

        i = i + 1
        if i != len(columns):
            print '    ' + str(c.name) + ' ' + column_type + ','
        else:
            print '    ' + str(c.name) + ' ' + column_type
    print ');'
