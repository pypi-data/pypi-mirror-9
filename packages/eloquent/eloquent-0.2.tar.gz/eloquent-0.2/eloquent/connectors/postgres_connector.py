# -*- coding: utf-8 -*-

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    pass

from .connector import Connector


class PostgresConnector(Connector):

    def connect(self, config):
        connection = self.get_api().connect(
            connection_factory=psycopg2.extras.DictConnection,
            **dict(filter(lambda x: x[0] != 'driver', config.items()))
        )
        connection.autocommit = True

        return connection

    def get_api(self):
        return psycopg2
