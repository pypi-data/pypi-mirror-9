#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas
import datetime
import sqlalchemy


_metadata = sqlalchemy.MetaData()


class SQLAlchemyStorage(object):

    def __init__(self, sqlengine, tablename_base='{reference}__{symbol}'):
        self.sqlengine = sqlengine
        self.tablename_base = tablename_base

    def save(self, dataframe, reference, symbol):
        tablename = self._tablename(reference, symbol)

        exists_table = self.sqlengine.has_table(tablename)
        if exists_table:
            start = _format_datetime(dataframe.index.values[0])
            end = _format_datetime(dataframe.index.values[-1], milis='0001')
            self.sqlengine.execute('DELETE FROM %s WHERE "index" >= "%s" AND "index" <= "%s"' % (tablename, start, end))

        dataframe.to_sql(tablename, self.sqlengine, if_exists='append')

        if not exists_table:
            table = sqlalchemy.Table(tablename, _metadata, autoload=True, autoload_with=self.sqlengine)
            sqlalchemy.Index('idx_index', table.c.index).create(self.sqlengine)

    def retrieve(self, reference, symbol, start=None, end=None):
        tablename = self._tablename(reference, symbol)

        exists_table = self.sqlengine.has_table(tablename)
        if not exists_table:
            return None

        sql_string = _generate_retrieval_sql(tablename, start=start, end=end)
        return pandas.read_sql_query(sql_string, self.sqlengine, parse_dates=['index'], index_col='index')

    def delete(self, reference, symbol):
        tablename = self._tablename(reference, symbol)

        exists_table = self.sqlengine.has_table(tablename)
        if not exists_table:
            return True

        self.sqlengine.execute('DROP TABLE "%s"' % tablename)
        return True

    def _tablename(self, reference, symbol):
        return self.tablename_base.format(reference=reference, symbol=symbol)


def _datetime_str(date):
    if date is None:
        return None
    return date.isoformat() if isinstance(date, datetime.datetime) else date


def _generate_retrieval_sql(tablename, start=None, end=None):
    base = 'SELECT * FROM "{table}" {where_clause} ORDER BY "index"'

    where_clause = ''
    if start or end:
        base_where_clause = 'WHERE {start_cond}{separator}{end_cond}'
        start_cond = '' if start is None else '"index" >= "%s"' % _datetime_str(start)
        end_cond = '' if end is None else '"index" <= "%s"' % _datetime_str(start)
        separator = ' AND ' if start and end else ''
        where_clause = base_where_clause.format(start_cond=start_cond,
                                                end_cond=end_cond,
                                                separator=separator)

    return base.format(table=tablename, where_clause=where_clause)


def _format_datetime(datetime64, milis='0'):
    return pandas.to_datetime(str(datetime64)).strftime('%Y-%m-%d %H:%M:%S.' + milis)
