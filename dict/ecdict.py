# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

'''读取 SQLite3 格式的字典'''

from sqlite3 import connect, Row
from typing import Union, Tuple


class ECDict:
    '''词典'''
    _SQL_GET = 'SELECT * FROM ecdict WHERE word = ?;'
    _SQL_GET_FUZZY = 'SELECT * FROM ecdict WHERE word LIKE ? LIMIT %d;'

    def __init__(self, database: str):
        self.closed = True
        self._conn = connect(database, isolation_level=None)
        self._conn.row_factory = Row
        self.closed = False

    def get(self, word: str):
        if self.closed:
            raise ValueError('Operation on closed dictionary.')
        return dict(self._conn.execute(self._SQL_GET, (word,)).fetchone())

    def get_fuzzy(self, word_fuzzy: str, limit: int):
        if self.closed:
            raise ValueError('Operation on closed dictionary.')
        return tuple(map(dict, self._conn.execute(
            self._SQL_GET_FUZZY % limit, (word_fuzzy + '%',)
        ).fetchall()))

    def __getitem__(self, key: Union[str, Tuple[str, int]]):
        if isinstance(key, tuple):
            return self.get_fuzzy(key[0], key[1])
        else:
            return self.get(key)

    def close(self):
        '''关闭词典'''
        if not self.closed:
            self._conn.close()
            self.closed = True

    def __del__(self):
        self.close()


def test():
    from pprint import pp
    d = ECDict(input('词典: '))
    print("d['abandon'] =>")
    pp(d['abandon'])
    print("d['aba', 5] =>")
    pp(d['abando', 5])


if __name__ == '__main__':
    test()
