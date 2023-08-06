# coding:utf-8

from .exceptions import UnacceptableResultError
from .queryformat import qformat
from .restructables import (RestructableList as RL,
                            RestructableDict as RD)


class Client(object):
    def __init__(self, dbapi, **kwargs):
        self.query_log = False

        self._dbapi = dbapi
        self._config = kwargs

        self._connection = None
        self._cursor = None

        self._result_cols = None
        self._result_rows = None
        self._lastrowid = None
        self._rowcount = None

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tb):
        self.close()

    def connection(self):
        if self._connection is None:
            self._connection = self._dbapi.connect(**self._config)
        return self._connection

    def cursor(self):
        if self._cursor is None:
            self._cursor = self.connection().cursor()
        return self._cursor

    def commit(self, close=True):
        self.connection().commit()

        if close:
            self.close()

        return self

    def rollback(self, close=True):
        self.connection().rollback()

        if close:
            self.close()

        return self

    def close(self):
        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None

        if self._connection is not None:
            self._connection.close()
            self._connection = None

        return self

    def exes(self, fmt, **kwargs):
        return self.exe(True, fmt, **kwargs)

    def exew(self, fmt, **kwargs):
        return self.exe(False, fmt, **kwargs)

    def exe(self, strong, fmt, **kwargs):
        q = qformat(fmt, **kwargs)

        if self.query_log:
            print('sqlew: {}'.format(q))

        try:
            self.cursor().execute(q)

        except Exception as e:
            self.close()
            raise e

        else:
            self._lastrowid = self.cursor().lastrowid
            self._rowcount = self.cursor().rowcount

            self._result_cols = [c[0] for c in self.cursor().description or []]
            self._result_rows = [r for r in self.cursor()]

            if not strong:
                self.close()

            return self

    def scalar(self, allow_none=True):
        if len(self._result_rows) > 0:
            return self._result_rows[0][0]

        else:
            return None if allow_none else self._unacceptable_result()

    def lastid(self, allow_zero=True):
        if allow_zero:
            return self._lastrowid or 0

        else:
            return self._lastrowid or self._unacceptable_result()

    def rowcount(self, allow_zero=True):
        if allow_zero:
            return self._rowcount or 0

        else:
            return self._rowcount or self._unacceptable_result()

    def first(self, allow_none=True):
        if len(self._result_rows) > 0:
            return RD(dict(zip(self._result_cols, self._result_rows[0])))

        else:
            return None if allow_none else self._unacceptable_result()

    def all(self, allow_empty=True):
        r = RL([
            RD(dict(zip(self._result_cols, r))) for r in self._result_rows
        ])

        if 0 < len(r):
            return r

        else:
            return [] if allow_empty else self._unacceptable_result()

    def _unacceptable_result(self):
        raise UnacceptableResultError()
