import argparse
import locale
import logging
import os
import sys
import traceback
from .parser import parse_file
from .db import generate_ddl, generate_import


def _show_error():
    """
    show system errors
    """
    et, ev, tb = sys.exc_info()

    print "Error Type: %s" % et
    print "Error Value: %s" % ev
    while tb:
        co = tb.tb_frame.f_code
        filename = str(co.co_filename)
        line_no = str(traceback.tb_lineno(tb))
        print '    %s:%s' % (filename, line_no)
        tb = tb.tb_next


def format_num(num):
    """Format a number according to given places.
    Adds commas, etc. Will truncate floats into ints!"""

    try:
        inum = int(num)
        return locale.format("%.*f", (0, inum), True)

    except (ValueError, TypeError):
        return str(num)


def get_max_width(table, index):
    """Get the maximum width of the given column index"""
    return max([len(format_num(row[index])) for row in table])


def pprint_table(out, table):
    """Prints out a table of data, padded for alignment
    @param out: Output stream (file-like object)
    @param table: The table to print. A list of lists.
    Each row must have the same number of columns. """

    col_paddings = []

    for i in range(len(table[0])):
        col_paddings.append(get_max_width(table, i))

    for row in table:
        # left col
        print >> out, row[0].ljust(col_paddings[0] + 1),
        # rest of the cols
        for i in range(1, len(row)):
            col = format_num(row[i]).ljust(col_paddings[i] + 2)
            print >> out, col,
        print >> out


def print_table(table):
    for row in table:
        print '\t'.join(row)


def command_info(raw_args, prog=None):
    if prog:
        parser = argparse.ArgumentParser(prog=prog)
    else:
        parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", required=False,
                        action="count", default=0,
                        help="show debugging info")

    group_delim = parser.add_mutually_exclusive_group(required=True)
    group_delim.add_argument('-C', '--comma', action='store_true', help='comma delimited file')
    group_delim.add_argument('-T', '--tab', action='store_true', help='tab delimited file')

    parser.add_argument('input_file', metavar='input_file',
                          help="parse data in FILE")

    args = parser.parse_args(raw_args)

    logging_level = logging.ERROR
    if args.verbose == 1:
        logging_level = logging.WARNING
    elif args.verbose == 2:
        logging_level = logging.INFO
    elif args.verbose > 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, format='%(message)s', stream=sys.stdout)

    logging.debug(args)

    input_file = os.path.abspath(args.input_file)
    delimiter = '\t' if args.tab else ','

    if not os.path.isfile(input_file):
        print "\nError: " + input_file + " is not a valid file."
        exit(1)

    locale.setlocale(locale.LC_NUMERIC, "")

    try:
        logging.debug("Parsing '{0}'...".format(input_file))
        columns = parse_file(input_file, delimiter)
        if columns:
            print 'File Summary:'
            table = [["INDEX", "COLUMN", "MAXVALUE", "MINVALUE", "MAXLEN", "MINLEN", "TYPE", "#VALS", "#EMPTY"]]

            for c in columns:
                simple_type = str(c.type).replace("<type '", "")
                simple_type = simple_type.replace("'>", "")
                table.append([str(c.index), str(c.name), str(c.max_value), str(c.min_value), str(c.max_length), str(c.min_length), simple_type.upper(), str(c.not_empty), str(c.empty)])

            pprint_table(sys.stdout, table)
        else:
            print 'Error parsing file!'
    except Exception, e:
        print str(e)
        _show_error()
        logging.error('ouch')


def command_sql(raw_args, prog=None):
    if prog:
        parser = argparse.ArgumentParser(prog=prog)
    else:
        parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", required=False,
                        action="count", default=0,
                        help="show debugging info")

    group_delim = parser.add_mutually_exclusive_group(required=True)
    group_delim.add_argument('-C', '--comma', action='store_true', help='comma delimited file')
    group_delim.add_argument('-T', '--tab', action='store_true', help='tab delimited file')


    group_dialect = parser.add_mutually_exclusive_group(required=True)
    group_dialect.add_argument('-M', '--MySQL', action='store_true', help='to specify MySQL')
    group_dialect.add_argument('-S', '--SQLite', action='store_true', help='to specify SQLite')


    parser.add_argument('-o', '--output', required=False,
                        default='.', metavar="output_directory",
                        help="output directory, defaults to current directory")

    parser.add_argument('-n', '--tablename', required=True,
                        metavar="table_name", help="generate SQL DML with supplied name as the table")


    parser.add_argument('input_file', metavar='input_file',
                          help="parse data in FILE")


    args = parser.parse_args(raw_args)

    logging_level = logging.ERROR
    if args.verbose == 1:
        logging_level = logging.WARNING
    elif args.verbose == 2:
        logging_level = logging.INFO
    elif args.verbose > 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, format='%(message)s', stream=sys.stdout)

    logging.debug(args)

    input_file = os.path.abspath(args.input_file)
    output_dir = args.output
    table_name = args.tablename
    delimiter = '\t' if args.tab else ','
    dialect = 'MYSQL' if args.MySQL else 'SQLITE'
    null_value = '\N' if args.MySQL else ''

    if args.output:
        output_dir = args.output

    if not os.path.isfile(input_file):
        print "\nError: " + input_file + " is not a valid file."
        exit(1)

    locale.setlocale(locale.LC_NUMERIC, "")

    try:
        output_file = "{0}.dat".format(os.path.abspath(os.path.join(output_dir, os.path.basename(input_file))))
        sql_file = "{0}.sql".format(os.path.abspath(os.path.join(output_dir, os.path.basename(input_file))))

        logging.debug("Parsing '{0}'\nGenerating '{1}'".format(input_file, output_file))

        columns = parse_file(input_file, delimiter, output_file, null_value, False)

        if columns != None:
            print 'File Summary:'
            table = [["INDEX", "COLUMN", "MAXVALUE", "MINVALUE", "MAXLEN", "MINLEN", "TYPE", "#VALS", "#EMPTY"]]

            for c in columns:
                simple_type = str(c.type).replace("<type '", "")
                simple_type = simple_type.replace("'>", "")
                table.append([str(c.index), str(c.name), str(c.max_value), str(c.min_value), str(c.max_length), str(c.min_length), simple_type.upper(), str(c.not_empty), str(c.empty)])

            pprint_table(sys.stdout, table)

            sql_ddl = generate_ddl(dialect, table_name, columns)
            sql_import = generate_import(dialect, table_name, columns, output_file, delimiter)

            try:
                sql_file_fd = open(sql_file, "w")
                sql_file_fd.write(sql_ddl)
                sql_file_fd.write('\n')
                sql_file_fd.write(sql_import)
                sql_file_fd.close()
            except:
                print 'Unable to generate SQL files!'
        else:
            print 'Error parsing file!'
    except Exception, e:
        print str(e)
        _show_error()
        logging.error('ouch')
