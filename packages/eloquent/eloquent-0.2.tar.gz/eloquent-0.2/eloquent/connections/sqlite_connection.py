# -*- coding: utf-8 -*-

from .connection import Connection
from ..query.processors.sqlite_processor import SQLiteQueryProcessor


class SQLiteConnection(Connection):

    def get_default_post_processor(self):
        return SQLiteQueryProcessor()

    def begin_transaction(self):
        self._connection.isolation_level = 'DEFERRED'

        super(SQLiteConnection, self).begin_transaction()

    def commit(self):
        if self._transactions == 1:
            self._connection.commit()
            self._connection.isolation_level = None

        self._transactions -= 1

    def rollback(self):
        if self._transactions == 1:
            self._transactions = 0

            self._connection.rollback()
            self._connection.isolation_level = None
        else:
            self._transactions -= 1
