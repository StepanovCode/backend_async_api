"""Load data from sqlite to postresql."""

import logging
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, fields
from itertools import islice

import psycopg2
from dataclass_models import switch_to_dataclass_by_table_name
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

logging.basicConfig(level=logging.INFO)


class SQLiteExtractor:
    """SQLite Reader."""

    def __init__(self, connection: sqlite3.Connection):
        self.curs = connection.cursor()
        self.curs.row_factory = sqlite3.Row
        self.tables_list = list(self._init_tables_list())

    def _init_tables_list(self):
        try:
            query = "SELECT * FROM sqlite_master where type='table';"
            self.curs.execute(query)
            while next_values := self.curs.fetchmany(20):
                for table in next_values:
                    yield table[1]
        except sqlite3.OperationalError as ex:
            logging.error("Error in _init_table_list >>> ", ex)

    def extract_by_table_name(self, table_name):
        try:
            query = 'SELECT * FROM {0};'.format(table_name)
            self.curs.execute(query)
            for data in self.curs.fetchall():
                yield dict(data)
        except sqlite3.OperationalError as ex:
            logging.error("Error in extract_by_table_name >>> ", ex)

    def extract_movies(self):
        for table_name in self.tables_list:
            yield [table_name, self.extract_by_table_name(table_name)]


class PostgresSaver:

    def __init__(self, _pg_conn: _connection):
        self.curs = _pg_conn.cursor()
        self.tables_list = list()

    def prepare_sql_query_template(self, table_name, table_fields):
        sql_keys = '(' + ', '.join([field.name for field in table_fields]) + ')'
        sql_values_template = '(' + ','.join(['%s' for _ in table_fields]) + ')'
        query = """INSERT INTO content.{0} {1}
                    VALUES {2}
                    ON CONFLICT DO NOTHING; """.format(
            table_name,
            sql_keys,
            sql_values_template
        )
        return query

    def dataclasses_to_list(self, dataclass_list: list):
        for element in dataclass_list:
            value = asdict(element).values()
            yield tuple(value)

    def save_full_table_data(self, table_name, values_generator,
                             batch_size):

        current_dataclass = switch_to_dataclass_by_table_name.get(table_name, None)
        if current_dataclass is None:
            raise KeyError('{0} dataclass dont exist, please confirm name'.format(table_name))

        query = self.prepare_sql_query_template(table_name, fields(current_dataclass))

        while data := list(islice(values_generator, batch_size)):
            dataclass_list = [current_dataclass(**record) for record in data]
            values = list(
                self.dataclasses_to_list(dataclass_list)
            )

            logging.info('Start insert... \nValues: {0} \nQuery: {1}'.format(values, query))
            self.curs.executemany(query, values)
            logging.info('-' * 30)

    def save_all_data(self, data, batch_size: int = 5):
        for table_name, table_data in data:
            self.save_full_table_data(table_name, table_data, batch_size)


def load_from_sqlite(connection: sqlite3.Connection, _pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres."""
    postgres_saver = PostgresSaver(_pg_conn)
    sqlite_extractor = SQLiteExtractor(connection)

    data = sqlite_extractor.extract_movies()
    postgres_saver.save_all_data(data)


@contextmanager
def open_sql3_db(file_name: str):
    conn = sqlite3.connect(file_name)
    try:
        logging.info("Creating SQLite3 connection")
        yield conn
    finally:
        logging.info("Closing SQLite3 connection")
        conn.commit()
        conn.close()


if __name__ == '__main__':

    dsl = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST', '127.0.0.1'),
        'port': os.environ.get('DB_PORT', 5433)
    }

    with open_sql3_db(file_name='db.sqlite') as cursor, \
            psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        logging.warning(pg_conn)
        load_from_sqlite(cursor, pg_conn)
