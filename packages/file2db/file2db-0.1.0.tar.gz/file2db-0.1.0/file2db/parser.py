import argparse
import csv
import locale
import logging
import os
import sys
import types

BAD_LEADING_CHARS = map(str, xrange(0, 10))
BAD_LEADING_CHARS.append('_')
EMPTY_COLUMN_VALS = ['na', 'n/a', '(none)', '(null)', 'null']


class File2DBParseError(Exception):
    pass


class Column(object):
    """ Simple class encapsulate meta data for a column

    """
    def __init__(self):
        self.name = None
        self.max_length = 0
        self.min_length = 0
        self.max_value = None
        self.min_value = None
        self.min_length_value = 0
        self.max_length_value = 0
        self.index = 0
        self.type = None
        self.empty = 0
        self.not_empty = 0


def parse_type(value):
    """
    Return converted value or raise File2DBParseError
    """
    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    if isinstance(value, basestring):
        return value.encode('ascii', 'ignore')

    raise File2DBParseError('Unknown type')


def fix_column_name(column_name):
    """
    Remove bad characters

    :param column_name:
    :return:
    """
    column_name = column_name.replace('.', '_')
    column_name = column_name.replace(' ', '_')

    # eliminate columns starting with bad characters
    while column_name[0] in BAD_LEADING_CHARS:
        column_name = column_name[1:]

    return column_name


def qdf(c):
    """
    qdf = quick data fix
    Strip the trailing and leading spaces and/or replace with None
    """
    s = str(c)
    s = s.strip()

    if len(s) > 1 and (s[0] == '"' or s[0] == '\'') and (s[-1] == '"' or s[-1] == '\''):
        s = s[1:]
        s = s[:-1]

    t = s.lower()

    if len(t) == 0 or t in EMPTY_COLUMN_VALS:
        s = None

    return s


def qdf_row(row):
    """
    qdf = quick data fix
    Strip the trailing and leading spaces and/or replace with None
    """
    return map(qdf, row)


def count_lines(filename):
    f = open(filename)
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    return lines


def parse_file(filename, output_file, delim='\t', null_value='\N'):
    """
    Parse a file and gather statistics about each column.
    """
    col_info = []
    num_lines = count_lines(filename)
    if num_lines == 0:
        logging.error("'{0}' contains no lines!!!".format(filename))
        exit()

    line = 0

    try:
        reader = csv.reader(open(filename, "rb"), delimiter=delim, quoting=csv.QUOTE_MINIMAL)
        if output_file:
            writer = csv.writer(open(output_file, "wb"), delimiter=delim, quoting=csv.QUOTE_MINIMAL)
        first_row = reader.next()
        i = 0
        line += 1

        logging.debug(first_row)

        # parse header or first row
        for h in first_row:
            c = Column()
            c.name = fix_column_name(h)
            c.index = i
            col_info.append(c)
            i += 1

        for row in reader:
            logging.debug(row)
            i = 0
            new_row = []
            for col in row:
                # handle nasty case where someone puts an extra delim at EOL
                if i >= len(col_info):
                    continue

                data = qdf(col)

                if data:
                    new_row.append(data)
                else:
                    new_row.append(null_value)

                c = col_info[i]

                # skip if no data
                if not data:
                    c.empty += 1
                else:
                    c.not_empty += 1
                    v = parse_type(data)
                    t = type(v)

                    dl = len(str(v))

                    if c.max_value:
                        c.max_length = dl if dl > c.max_length else c.max_length
                        c.max_value = v if v > c.max_value else c.max_value
                    else:
                        c.max_value = v
                        c.max_length = dl

                    if c.min_value:
                        c.min_length = dl if dl < c.min_length else c.min_length
                        c.min_value = v if v < c.min_value else c.min_value
                    else:
                        c.min_value = v
                        c.min_length = dl

                    if c.type == types.FloatType:
                        if t == str:
                            c.type = t
                    elif c.type == types.StringType:
                        pass
                    else:
                        c.type = t

                col_info[i] = c

                i += 1
            line += 1

            if output_file:
                writer.writerow(new_row)
    except Exception, inst:
        print "Line number: " + str(line)
        return None

    return col_info


