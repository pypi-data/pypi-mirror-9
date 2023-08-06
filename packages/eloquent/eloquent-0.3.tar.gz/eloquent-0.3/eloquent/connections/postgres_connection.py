# -*- coding: utf-8 -*-

from ..utils import PY2
from .connection import Connection
from ..query.grammars.postgres_grammar import PostgresQueryGrammar
from ..query.processors.postgres_processor import PostgresQueryProcessor


class PostgresConnection(Connection):

    def get_default_query_grammar(self):
        return PostgresQueryGrammar()

    def get_default_post_processor(self):
        return PostgresQueryProcessor()

    def begin_transaction(self):
        self._connection.autocommit = False

        super(PostgresConnection, self).begin_transaction()

    def commit(self):
        if self._transactions == 1:
            self._connection.commit()
            self._connection.autocommit = True

        self._transactions -= 1

    def rollback(self):
        if self._transactions == 1:
            self._transactions = 0

            self._connection.rollback()
            self._connection.autocommit = True
        else:
            self._transactions -= 1

    def _get_cursor_query(self, query, bindings):
        if not hasattr(self._cursor, 'query'):
            return super(PostgresConnection, self)._get_cursor_query(query, bindings)

        if PY2:
            return self._cursor.query

        return self._cursor.query.decode()
