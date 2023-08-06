# Copyright 2011-2015 梅濁酒(umedoblock)

import sys
import sqlite3
import configparser
import os, sys
from collections import namedtuple
from collections import OrderedDict

_here = os.path.abspath(__file__)
_parent_dir = os.path.join(os.path.dirname(_here), "..")
# print("_parent_dir =", _parent_dir)
sys.path.append(_parent_dir)

from iasap.lib import logger

class GeneralSQLConnection(object):
    def __init__(self, conn):
        self.conn = conn
        try:
            self.create_namedtuples_table()
        except sqlite3.OperationalError:
            pass
        logger.info('GeneralSQL(self=0x{:x}, conn=0x{:x}) done.'. \
                          format(id(self), id(conn)))

    def commit(self):
        self.conn.commit()

    def close(self):
        self.commit()
        self.conn.close()
        logger.info('close {}.'.format(self))

    def create_namedtuples_table(self):
        conn = self.conn
        table_name = '__namedtuples__'
        sql = '''
            create table __namedtuples__
            (
                id integer primary key,
                typename uniq text,
                field_names text
            )'''
        logger.debug(sql)
        conn.execute(sql)
        conn.commit()
        logger.info('created __namedtuples__ table.')

        od = OrderedDict()
        od['id'] = None
        od['typename'] = table_name
        od['field_names'] = ''
        od['field_names'] = ' '.join(od.keys())
        logger.debug('od.keys() = {}'.format(od.keys))
        self.insert('__namedtuples__', od)
        logger.info('1: inserted __namedtuples__ table info '
                    'to __namedtuples__ table.')

    def create_table(self, table_info):
        cur = self.conn.cursor()
        table_name = table_info["table_name"]
        columns = []
        for column_name, explain in table_info.items():
            if column_name == "table_name":
                continue
            column = ' '.join([column_name, explain])
            columns += [column]
        sql = 'create table {} ({})'.format(table_name, ', '.join(columns))
        logger.debug(sql)
        cur.execute(sql)
        logger.info('created {} table.'.format(table_name))

        # print(list(table_info.keys()))
        od = OrderedDict()
        od['id'] = None
        od['typename'] = table_name
        L = list(table_info.keys())
        logger.debug('list(table_info.keys()) = {}'.format(L))
        L.remove("table_name")
        od['field_names'] = ' '.join(L)
        self.insert('__namedtuples__', od)
        logger.info('2: inserted {} table info '
                    'to __namedtuples__ table.'.format(table_name))

    def insert(self, table_name, columns=None):
        cur = self.conn.cursor()
        hatenas = '({})'.format(', '.join('?' * len(columns.values())))
        sql_ = 'insert into {} {} values '.format(table_name, \
                                                  tuple(columns.keys()))
        values = tuple(columns.values())
        logger.debug(sql_ + str(values))
        cur.execute(sql_ + hatenas, values)
        cur.close()

    def select(self, sql, values=None, max_rows=0):
        logger.debug(sql)
        logger.debug(values)

        return NamedRow(self.conn, sql, values, max_rows)
#       named_rows = []
#       rows = cur.fetchall()
#       cur.close()
#       for row in rows:
#           named_row = namedtup(*row)
#           named_rows.append(named_row)

#       return named_rows

class NamedRow(object):
    def __init__(self, conn, sql, values=None, max_rows=0):
        self.sql = sql
        self.values = values
        self.cur = conn.cursor()
        self.max_rows = max_rows
        self._i = 0
        sp = sql.split()
        table_name_index = sp.index('from') + 1
        table_name = sp[table_name_index]

        namedtup = self._get_namedtuple(table_name)

        if self.values:
            result = self.cur.execute('select ' + sql, self.values)
        else:
            result = self.cur.execute('select ' + sql)
        self.namedtup = namedtup
        logger.info('NamedRow(self={})'.format(self))

    def _get_namedtuple(self, typename):
        if not hasattr(self.__dict__, typename):
            cur = self.cur
            sql = ('select * from __namedtuples__ where '
                   'typename = "{}"').format(typename)
            logger.debug(sql)
            result = cur.execute(sql)
            logger.info('got {} __namedtuples__ info.'.format(typename))
            row = cur.fetchone()
            if not row:
                raise ValueError("typename={} is not in __namedtuples__")
            field_names = row[2]
            namedtup = namedtuple(typename, field_names)
            self.__dict__[typename] = namedtup
        else:
            namedtup = self.__dict__[typename]
        return namedtup

    def __iter__(self):
        return self

    def __next__(self):
        self._i += 1
        row = None
        if not self.max_rows or self._i <= self.max_rows:
            row = self.cur.fetchone()
        if row:
            logger.debug("row = {}".format(row))
            logger.debug("self.namedtup = {}".format(self.namedtup))
            return self.namedtup(*row)
        else:
            self.cur.close()
            raise StopIteration

if __name__ == '__main__':
    import os
    abs_path = os.path.abspath(__file__)
    print(abs_path)
    dname = os.path.dirname(abs_path)
    print(dname)
    conf_path = os.path.join(dname, "iasap.conf")
    config = configparser.ConfigParser()
    config.read_file(open(conf_path), 'iasap')

    path = ':memory:'
    conn = sqlite3.connect(path)

    conn = GeneralSQLConnection(conn)
    conn.create_table(config['schema'])
    for id in range(0, 4):
        column = \
            {'id': None, 'key': 'key' + str(id), 'value': 'value' + str(id)}
        conn.insert('iasap', column)
        print('id =', id, column)
#   conn.commit()

    named_rows = conn.select('* from iasap')
    print('named_rows =', named_rows)
    for i, named_row in enumerate(named_rows):
        nr = named_row
        print('i =', i, nr)
      # print('i =', i, nr.id, nr.key, nr.value)
    conn.close()
