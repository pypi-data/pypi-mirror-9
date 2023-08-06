# Copyright 2011-2015 梅濁酒(umedoblock)

import sqlite3
import argparse
import configparser
import re
import os

import lib
lib.sys_path_append_parent_dir(__file__, 2)
from iasap.sql import GeneralSQLConnection
from iasap.lib import start_logger, logger

from eijiroXXX import EijiroXXX

start_logger(os.path.basename(__file__), os.path.curdir, logger.INFO)

parser = argparse.ArgumentParser(description='make eijiroXXX database.')

parser.add_argument('--txtpath', metavar='f', dest='txtpath',
                    required=True,
                    help='eijiroXXX.txt path')
parser.add_argument('--table-name', metavar='t', dest='table_name',
                    nargs='?',
                    default='eijiroXXX',
                    help='default: eijiroXXX')
parser.add_argument('--dbpath', metavar='f', dest='dbpath',
                    nargs='?',
                    default=EijiroXXX.DEFAULTS["dbpath"],
                    help='default: {}'.format(EijiroXXX.DEFAULTS["dbpath"]))
parser.add_argument('--conf', metavar='f', dest='conf',
                    nargs='?',
                    default=EijiroXXX.DEFAULTS["conf"],
                    help='default: {}'.format(EijiroXXX.DEFAULTS["conf"]))
parser.add_argument('--debug', dest='debug',
                   action='store_true', default=False,
                   help='use debug ? (default: False)')

args = parser.parse_args()
txtpath = args.txtpath
print('args.txtpath =', txtpath)
if not txtpath:
    raise ValueError('txtpath muse be available txtpath')
dbpath = args.dbpath
print('args.dbpath =', dbpath)
if not dbpath:
    raise ValueError('dbpath muse be available path')
conf = args.conf
print('args.conf =', conf)
if not conf:
    raise ValueError('conf muse be available path')

txtpath = os.path.expanduser(txtpath)
dbpath = os.path.expanduser(dbpath)
confpath = os.path.expanduser(conf)

if os.path.isfile(dbpath):
    print("dbpath として指定した path には既に、file が存在します。")
    print(dbpath)
    s = input("を削除しますか？ 削除するなら、yes を入力してください。->: ")

    if s.lower() == "yes":
        os.remove(dbpath)
        print("dbpath={}\nを削除しました。".format(dbpath))
    else:
        raise ValueError("起動 option --dbpath=xxx に適切な path を入力して下さい。")

config = configparser.ConfigParser()
config.read(confpath)
conn_sqlite3 = sqlite3.connect(dbpath)
conn = GeneralSQLConnection(conn_sqlite3)
try:
    conn.create_table(config['schema'])
except sqlite3.OperationalError as raiz:
    if raiz.args[0] != 'table {} already exists'.format(args.table_name):
        raise sqlite3.OperationalError(*raiz.args)

print()
print("dbpath={}\nに、sqlite3 形式の db を作成しています。".format(dbpath))
with open(txtpath, encoding='utf8') as f:
    for l in f:
        l = l.strip()
      # print(l)
        key, value = re.findall('(.*) /// (.*)', l)[0]
      # prefix, v0 = parse_key(key)
      # v1, suffix = parse_value(value)
      # print(prefix, v0, v1, suffix, sep='|')
      # print(key, value, sep='|')
        column = \
            {'id': None, 'key': key, 'value': value}
        conn.insert(args.table_name, column)
conn.close()
