# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

import platform
import sqlite3
import traceback
import itertools

_SQL_SELECT_EQUAL = 'SELECT word, phonetic, collins, oxford, translation FROM stardict WHERE word = ? '
_SQL_SELECT_LIKE = 'SELECT word, collins, oxford FROM stardict WHERE word LIKE ? '
_SQL_AND_COLLINS = 'AND collins > 0 '
_SQL_LIMIT_1 = 'LIMIT 1 '
_SQL_LIMIT_5 = 'LIMIT 5 '
SQL_EQUAL_COLLINS_1 = _SQL_SELECT_EQUAL + _SQL_AND_COLLINS + _SQL_LIMIT_1 + ';'
SQL_LIKE_COLLINS_5 = _SQL_SELECT_LIKE + _SQL_AND_COLLINS + _SQL_LIMIT_5 + ';'
SQL_EQUAL_1 = _SQL_SELECT_EQUAL + _SQL_LIMIT_1 + ';'
SQL_LIKE_5 = _SQL_SELECT_LIKE + _SQL_LIMIT_5 + ';'

# COLUMN = dict(zip(('def'
#     'id', 'word', 'sw', 'phonetic', 'definition', 'translation', 'pos', 'collins', 'oxford', 'tag', 'bnc', 'frq', 'exchange', 'detail', 'audio',
# ), itertools.count()))


def main():
    print(
        f'ECDICTIONARY 0.1.0 [SQLite {sqlite3.sqlite_version}, Python {platform.python_version()} (sqlite3 {sqlite3.version})]')
    print('版权所有 © NKID00 2020\n')

    with sqlite3.connect('./ultimate.db') as connection:
        sql_equal = SQL_EQUAL_COLLINS_1
        sql_like = SQL_LIKE_COLLINS_5
        while True:
            try:
                input_s = input('>>> ')
                if input_s.startswith('.'):
                    input_s = input_s[1:]
                    if input_s == 'help':
                        print(
                            'foo     查询单词(仅柯林斯词频分级的单词)\n'
                            'foo%    补全单词(仅柯林斯词频分级的单词)\n'
                            '~foo    查询单词\n'
                            '~foo%   补全单词\n'
                            '.help   显示此帮助\n'
                            '.exit   退出\n'
                        )
                    elif input_s == 'exit':
                        return
                    else:
                        print('命令错误')
                    continue

                if input_s.startswith('~'):
                    input_s = input_s[1:]
                    sql_equal = SQL_EQUAL_1
                    sql_like = SQL_LIKE_5
                else:
                    sql_equal = SQL_EQUAL_COLLINS_1
                    sql_like = SQL_LIKE_COLLINS_5

                if input_s.endswith('%'):
                    input_s = input_s[:-1]
                    s = ''
                    for row in connection.execute(sql_like, (input_s + '%',)):
                        s += row[0]
                        if row[1]:
                            s += f' [C{row[1]}]'
                        if row[2]:
                            s += f' [O]'
                        s += '\n'
                    if s:
                        print(s)
                else:
                    for row in connection.execute(sql_equal, (input_s,)):
                        s = row[0]
                        if row[1]:
                            s += f' /{row[1]}/'
                        if row[2]:
                            s += f' [C{row[2]}]'
                        if row[3]:
                            s += ' [O]'
                        s += f'\n{row[4]}\n'
                        print(s)
            except Exception:
                traceback.print_exc()


if __name__ == "__main__":
    main()
