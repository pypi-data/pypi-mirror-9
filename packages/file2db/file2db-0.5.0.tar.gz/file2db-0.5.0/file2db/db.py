import types


def generate_ddl(dialect, table_name, columns):
    if dialect == 'MYSQL':
        return generate_mysql_ddl(table_name, columns)
    elif dialect == 'SQLITE':
        return generate_sqlite_ddl(table_name, columns)
    else:
        raise ValueError('Unknown dialect')


def generate_import(dialect, table_name, columns, data_file, delimiter):
    if dialect == 'MYSQL':
        return generate_mysql_import(table_name, columns, data_file, delimiter)
    elif dialect == 'SQLITE':
        return generate_sqlite_import(table_name, columns, data_file, delimiter)
    else:
        raise ValueError('Unknown dialect')


def generate_mysql_ddl(table_name, columns):
    sql = []
    sql.append('DROP TABLE IF EXISTS tmp_{0};'.format(table_name))
    sql.append('CREATE TABLE tmp_{0} ('.format(table_name))
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

        i += 1
        if i != len(columns):
            sql.append('    {0} {1},'.format(c.name, column_type))
        else:
            sql.append('    {0} {1}'.format(c.name, column_type))
    sql.append(');')

    sql.append('DROP TABLE IF EXISTS {0};'.format(table_name))
    sql.append('CREATE TABLE {0} ('.format(table_name))
    sql.append('    _{0}_id INT(10) unsigned NOT NULL AUTO_INCREMENT,'.format(table_name))
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

        sql.append('    {0} {1},'.format(c.name, column_type))
    sql.append('    PRIMARY KEY (_{0}_id)'.format(table_name))
    sql.append(');')
    return '\n'.join(sql)


def generate_mysql_import(table_name, columns, data_file, delimiter):
    sql = []
    column_names = []
    for c in columns:
        column_names.append(c.name)
    if delimiter == '\t':
        sql.append("LOAD DATA INFILE '{0}' INTO TABLE tmp_{1} FIELDS TERMINATED BY '\\t';".format(data_file, table_name))
    else:
        sql.append("LOAD DATA INFILE '{0}' INTO TABLE tmp_{1} FIELDS TERMINATED BY ',';".format(data_file, table_name))
    sql.append("INSERT INTO {0} SELECT NULL, {1} FROM tmp_{2};".format(table_name, ','.join(column_names), table_name))
    sql.append("DROP TABLE tmp_{0};".format(table_name));
    return '\n'.join(sql)


def generate_sqlite_ddl(table_name, columns):
    sql = []
    sql.append('DROP TABLE IF EXISTS tmp_{0};'.format(table_name))
    sql.append('CREATE TABLE tmp_{0} ('.format(table_name))

    i = 0
    for c in columns:
        column_type = 'TEXT'
        if c.type == types.FloatType:
            column_type = 'REAL'
        elif c.type == types.StringType:
            column_type = 'TEXT'
        else:
            column_type = 'INTEGER'

        i += 1
        if i != len(columns):
            sql.append('    {0} {1},'.format(c.name, column_type))
        else:
            sql.append('    {0} {1}'.format(c.name, column_type))
    sql.append(');')

    sql.append('DROP TABLE IF EXISTS {0};'.format(table_name))
    sql.append('CREATE TABLE {0} ('.format(table_name))
    sql.append('    _{0}_id INTEGER PRIMARY KEY AUTOINCREMENT,'.format(table_name))
    i = 0
    for c in columns:
        column_type = 'TEXT'
        if c.type == types.FloatType:
            column_type = 'REAL'
        elif c.type == types.StringType:
            column_type = 'TEXT'
        else:
            column_type = 'INTEGER'

        i += 1
        if i != len(columns):
            sql.append('    {0} {1},'.format(c.name, column_type))
        else:
            sql.append('    {0} {1}'.format(c.name, column_type))
    sql.append(');')
    return '\n'.join(sql)

def generate_sqlite_import(table_name, columns, data_file, delimiter):
    sql = []
    if delimiter == '\t':
        sql.append('.separator \\t')
    else:
        sql.append('.separator ,')
    column_names = []
    for c in columns:
        column_names.append(c.name)
    sql.append(".import {0} tmp_{1}".format(data_file, table_name))
    sql.append("INSERT INTO {0} SELECT NULL, {1} FROM tmp_{2};".format(table_name, ','.join(column_names), table_name))
    sql.append("DROP TABLE tmp_{0};".format(table_name));
    return '\n'.join(sql)


