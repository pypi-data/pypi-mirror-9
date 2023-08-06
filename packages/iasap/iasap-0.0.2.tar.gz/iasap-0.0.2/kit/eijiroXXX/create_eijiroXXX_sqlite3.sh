# Copyright 2011-2015 梅濁酒(umedoblock)

DB_PATH=./eijiroXXX.sqlite3

# 英辞郎の一行形式の text file を sqlite3 形式の db に変換。
OS_SYS_EXECUTE ./make_db.py \
               --txtpath=./eijiroXXX.txt \
               --dbpath=${DB_PATH}

echo
echo sqlite3 形式の db 作成後の大きさ
ls -lh ${DB_PATH}

# index 作成。
echo eijiroXXX table 用の index 作成中
time sqlite3 ${DB_PATH} < ./create_index_on_eijiroXXX.sql

echo
echo index 作成後の大きさ
ls -lh ${DB_PATH}

echo
sqlite3 ${DB_PATH} "select * from __namedtuples__"
# 1|__namedtuples__|id typename field_names
# 2|eijiroXXX|id key value
sqlite3 ${DB_PATH} "select count(*) from eijiroXXX"
# 1637342
sqlite3 ${DB_PATH} "select * from eijiroXXX limit 10"
