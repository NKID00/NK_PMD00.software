# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

'''读取 SQLite3 格式的 ECDICT'''

from sqlite3 import connect, Row
from operator import itemgetter
from collections import defaultdict


class ECDict:
    '''ECDICT 辞典'''
    _SQL_GET = 'SELECT * FROM ecdict WHERE word = ?;'
    _SQL_GET_FUZZY = 'SELECT * FROM ecdict WHERE word LIKE ?'
    _SQL_NO_PHRASES = ' AND word NOT LIKE "%% %%"'
    _SQL_NO_COLLINS0 = ' AND collins > 0'
    _SQL_NO_ABBR = (
        ' AND (\n'
        '    translation LIKE "%%" + CHAR(10) + "%%"\n'  # 有换行
        '    OR translation NOT LIKE "%%abbr.%%"\n'  # 或者没有 'abbr.'
        ')'
    )
    _SQL_NO_NETWORK_DEFINITION = (
        ' AND (\n'
        '    translation LIKE "%%" + CHAR(10) + "%%"\n'  # 有换行
        '    OR translation NOT LIKE "%%[网络]%%"\n'  # 或者没有 '[网络]'
        ')'
    )
    _SQL_NO_PLACE_NAME = (
        ' AND (\n'
        '    translation LIKE "%%" + CHAR(10) + "%%"\n'  # 有换行
        '    OR translation NOT LIKE "%%[地名]%%"\n'  # 或者没有 '[地名]'
        ')'
    )
    _SQL_NO_MEDICAL = (
        ' AND (\n'
        '    translation LIKE "%%" + CHAR(10) + "%%"\n'  # 有换行
        '    OR translation NOT LIKE "%%[医]%%"\n'  # 或者没有 '[医]'
        ')'
    )
    _SQL_NO_MEDICINE = (
        ' AND (\n'
        '    translation LIKE "%%" + CHAR(10) + "%%"\n'  # 有换行
        '    OR translation NOT LIKE "%%[药]%%"\n'  # 或者没有 '[药]'
        ')'
    )
    _SQL_NO_CHEMICAL = (
        ' AND (\n'
        '    translation LIKE "%%" + CHAR(10) + "%%"\n'  # 有换行
        '    OR translation NOT LIKE "%%[化]%%"\n'  # 或者没有 '[化]'
        ')'
    )
    _SQL_NO_PAREN = ' AND word NOT LIKE "%%(%%" AND word NOT LIKE "%%（%%"'
    _SQL_LIMIT_SEMICOLON = ' LIMIT %d;'

    def __init__(self, database: str, settings: dict):
        self.closed = True
        self._conn = connect(database, isolation_level=None)
        self._conn.row_factory = Row
        self.closed = False
        self._settings = settings

    def get(self, word: str):
        if self.closed:
            raise ValueError('Operation on closed dictionary.')
        return dict(self._conn.execute(self._SQL_GET, (word,)).fetchone())

    def find(self, word_fuzzy: str, limit: int = 10):
        if self.closed:
            raise ValueError('Operation on closed dictionary.')
        sql = self._SQL_GET_FUZZY
        settings = defaultdict(lambda: False, self._settings)
        if not settings['词组']:
            sql += self._SQL_NO_PHRASES
        if not settings['柯林斯 0 星']:
            sql += self._SQL_NO_COLLINS0
        if not settings['缩写 abbr.']:
            sql += self._SQL_NO_ABBR
        if not settings['[网络]']:
            sql += self._SQL_NO_NETWORK_DEFINITION
        if not settings['[地名]']:
            sql += self._SQL_NO_PLACE_NAME
        if not settings['[医]']:
            sql += self._SQL_NO_MEDICAL
        if not settings['[药]']:
            sql += self._SQL_NO_MEDICINE
        if not settings['[化]']:
            sql += self._SQL_NO_CHEMICAL
        if not settings['包含括号']:
            sql += self._SQL_NO_PAREN
        sql += self._SQL_LIMIT_SEMICOLON
        return list(map(itemgetter('word'), self._conn.execute(
            sql % limit, (word_fuzzy + '%',)
        ).fetchall()))

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return self.find(key[0], key[1])
        else:
            return self.get(key)

    def close(self):
        '''关闭辞典'''
        if not self.closed:
            self._conn.close()
            self.closed = True

    def __del__(self):
        self.close()


def test():
    from pprint import pp
    d = ECDict('ecdict.db', {})
    print("d['abando', 5] =>")
    pp(d['abando', 5])
    print("d['abandon'] =>")
    pp(d['abandon'])
    print("d['abandon anchor'] =>")
    pp(d['abandon anchor'])


if __name__ == '__main__':
    test()
