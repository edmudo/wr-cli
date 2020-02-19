from resources import ResourceQuery as Q

import csv
import sqlite3
import os

from enum import Enum


class DatabaseError(Enum):
    NO_SUCH_TABLE = 0
    NO_SUCH_COLUMN = 1
    UNKNOWN_ERROR = 2
    MISSING_DATA = 3
    MISSING_SCHEMA = 4


class Database:
    def __init__(self, data_dir=None, db_path=None, schema_path=None, limit=10):
        if data_dir is None:
            data_dir = 'data'

        if db_path is None:
            db_path = 'wine.db'

        if schema_path is None:
            directory = os.path.dirname(__file__)
            schema_path = f'{directory}/schema.txt'

        self.data_path = data_dir
        self.schema_path = schema_path

        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.close = self.connection.close

        self.limit = limit

    def load_data(self):
        try:
            # Read in create statements for each table from schema.txt file
            with open(self.schema_path, "r") as schema_file:
                script = schema_file.read()
                self.connection.executescript(script)
        except FileNotFoundError as e:
            e.args = (*e.args, DatabaseError.MISSING_SCHEMA)
            raise e

        # Read in data for each table from csv files
        wine_array = self._build_query_args(f'{self.data_path}/Wine.csv')
        review_array = self._build_query_args(f'{self.data_path}/Review.csv')
        reviewer_array = self._build_query_args(f'{self.data_path}/Reviewer.csv')

        # Insert data into wine, review and reviewer tables
        self.connection.executemany(Q.INSERT_WINE, wine_array)
        self.connection.executemany(Q.INSERT_REVIEW, review_array)
        self.connection.executemany(Q.INSERT_REVIEWER, reviewer_array)

        self.connection.commit()

    def _build_query_args(self, path):
        args = []

        try:
            with open(path) as f:
                csv_reader = csv.reader(f)
                next(csv_reader)
                for row in csv_reader:
                    args.append(row)
        except FileNotFoundError as e:
            e.args = (*e.args, DatabaseError.MISSING_DATA)
            raise e

        return args

    def do_query(self, kw, **kwargs):
        try:
            if kw['_keyword'] == "wine":
                return self._execute_query(kw, Q.SELECT_WINE, **kwargs)

            if kw['_keyword'] == "review":
                return self._execute_query(kw, Q.SELECT_REVIEW, **kwargs)

            if kw['_keyword'] == "reviewer":
                return self._execute_query(kw, Q.SELECT_REVIEWER, **kwargs)
        except sqlite3.OperationalError as e:
            if 'table' in str(e):
                raise ValueError(DatabaseError.NO_SUCH_TABLE)
            if 'column' in str(e):
                raise ValueError(DatabaseError.NO_SUCH_COLUMN)
            raise ValueError(DatabaseError.UNKNOWN_ERROR)

    def _get_limit_string(self, page_offset):
        offset = max(self.limit * (page_offset - 1), 0)
        return Q.ADDON_LIMIT.format(self.limit, offset)

    def _execute_query(self, kw, query, page_offset=0):
        add_on_string = self._add_on(kw)
        offset_string = self._get_limit_string(page_offset)

        query = query + add_on_string + offset_string
        select = self.connection.execute(query)
        results = select.fetchall()

        return results

    def _add_on(self, kw):
        key_values = []
        for key, value in kw.items():
            if key == "_keyword":
                continue
            if isinstance(value, tuple):
                operator, value = value
            else:
                operator = '='
            key_values.append(f"{key}{operator}'{value}'")
        if key_values:
            add_on_string = " WHERE " + " AND ".join(key_values)
        else:
            add_on_string = ""
        return add_on_string
