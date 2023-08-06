__version__ = '1.1.1'

from argparse import ArgumentParser
import atexit
import getpass
import re

from MySQLdb import connect
from MySQLdb.cursors import DictCursor

from .SchemaInformation import SchemaInformation

# TODO: Maybe monitor float types?
def monitor():
    # TODO: maybe add phpmyadmin here?
    excluded_db = ['mysql', 'information_schema', 'performance_schema']
    included_db = []

    arg_parser = ArgumentParser()
    arg_parser.add_argument('--username', '-u', default='root',
                            help='MySQL username')
    arg_parser.add_argument('--password', '-p', default='',
                            help='MySQL password', nargs='?')
    arg_parser.add_argument('--host', default='localhost',
                            help='MySQL host')
    arg_parser.add_argument('--threshold', '-t', default=0.8, type=float,
                            help="""The alerting threshold (ex: 0.8 means"""
                                 """ alert when a column max value is 80%%"""
                                 """ of the max possible value""")
    arg_parser.add_argument('--exclude', '-e', nargs='+', default=[],
                            help='Database to exclude separated by a comma')
    arg_parser.add_argument('--db', '-d', required=False, nargs='+',
                            help="""Databases to analyse separated by a"""
                                 """ comma (default all)""")

    args = arg_parser.parse_args()
    args.exclude += excluded_db

    password = args.password
    if args.password is None:
        password = getpass.getpass()

    try:
        # MySQL connection
        db = connect(host=args.host,
                     user=args.username,
                     passwd=password,
                     cursorclass=DictCursor)
    except Exception as error:
        print str(error)
        exit(2)

    atexit.register(db.close)

    # Configure schema analyser
    schema = SchemaInformation(db)

    # Handle database inc/exl parameters
    schema.excluded_db = args.exclude
    if args.db is not None:
        schema.included_db = args.db

    # Disabling InnoDB statistics for performances
    schema.init_mysql_session()

    print "Start"

    # Get column definitions
    columns = schema.get_columns_by_table()

    for definition in columns:
        # Get all max values for a given table

        columns_max_values = schema.get_table_max_values(
            definition['TABLE_SCHEMA'], definition['TABLE_NAME'],
            definition['COLUMN_NAMES'].split(','))

        table_cols = zip(definition['COLUMN_NAMES'].split(','),
                         definition['COLUMN_TYPES'].split(','))

        # Process column by column
        for name, full_type in table_cols:
            # Parsing column data to retrieve details, max values ...
            type, unsigned = re.split('\\s*\(\d+\)\s*', full_type)
            max_allowed = schema.get_type_max_value(type, unsigned)
            current_max_value = columns_max_values[name]

            # Calculate max values with threshold and comparing
            if (current_max_value >= int(max_allowed * args.threshold)):
                percent = round(
                    float(current_max_value) / float(max_allowed) * 100, 2)
                resting = max_allowed - current_max_value
                print ("""WARNING: (%s %s) %s.%s.%s max value is %s near"""
                       """(allowed=%s%%, resting=%s)""") % (
                          type, unsigned, definition['TABLE_SCHEMA'],
                          definition['TABLE_NAME'], name, current_max_value,
                          percent, resting)
    print "Done"
