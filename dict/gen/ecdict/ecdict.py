# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

from csv import DictReader
from sqlite3 import connect, Cursor
from os.path import exists
from os import remove
from time import time


def create_table(cursor: Cursor):
    '''创建表'''
    cursor.execute(
        '''CREATE TABLE ecdict (
            word        VARCHAR(64) PRIMARY KEY -- 单词
                        COLLATE NOCASE -- 比较时不区分大小写
                        NOT NULL UNIQUE,
            phonetic    VARCHAR(64) DEFAULT(NULL), -- 音标
            pos         VARCHAR(32) DEFAULT(NULL), -- 词性比率
            definition  TEXT DEFAULT(NULL), -- 英文定义
            translation TEXT DEFAULT(NULL), -- 中文翻译
            collins     INTEGER DEFAULT(0), -- 柯林斯星级（0-5）
            oxford      INTEGER DEFAULT(0), -- 牛津核心词汇（0-1）
            gk          INTEGER DEFAULT(0), -- 高考范围（0-1）
            cet4        INTEGER DEFAULT(0), -- 四级范围（0-1）
            cet6        INTEGER DEFAULT(0), -- 六级范围（0-1）
            ky          INTEGER DEFAULT(0), -- 考研范围（0-1）
            plural      VARCHAR(32) DEFAULT(NULL), -- 名词复数形式
            comparative VARCHAR(32) DEFAULT(NULL), -- 形容词比较级
            superlative VARCHAR(32) DEFAULT(NULL), -- 形容词最高级
            present     VARCHAR(32) DEFAULT(NULL), -- 动词现在分词
            past        VARCHAR(32) DEFAULT(NULL), -- 动词过去式
            perfect     VARCHAR(32) DEFAULT(NULL), -- 动词过去分词
            third       VARCHAR(32) DEFAULT(NULL), -- 动词第三人称单数
            lemma       VARCHAR(32) DEFAULT(NULL)  -- 词根
        );'''
    )


def copy_item(target: dict, source: dict, key, target_key=None, default=None, factory=None):
    '''如果不是空的就复制'''
    if target_key is None:
        target_key = key
    if key in source and source[key] != '':
        if factory is not None:
            target[target_key] = factory(source[key])
        else:
            target[target_key] = source[key]
    elif default is not None:
        target[target_key] = default


def set_item(target: dict, source: tuple, key, value):
    '''如果存在就赋值'''
    if key in source:
        target[key] = value


def split_exchange(exchange: str) -> dict:
    '''分割词形变化表'''
    if exchange == '':
        return {}
    else:
        return dict(s.split(':') for s in exchange.split('/'))


def row2dict(row) -> dict:
    # 复制必需字段
    value = {'word': row['word']}

    # 复制简单字段
    for key in (
        'word', 'phonetic', 'definition', 'translation', 'pos'
    ):
        copy_item(value, row, key)

    # 复制数字字段
    for key in (
        'collins', 'oxford'
    ):
        copy_item(value, row, key, factory=int)

    # 复制标签
    tags = row['tag'].split(' ')
    for tag in tags:
        set_item(value, ('gk', 'cet4', 'cet6', 'ky'), tag, 1)

    # 复制词形变化
    exchanges = split_exchange(row['exchange'])
    copy_item(value, exchanges, 's', 'plural')
    copy_item(value, exchanges, 'r', 'comparative')
    copy_item(value, exchanges, 't', 'superlative')
    copy_item(value, exchanges, 'i', 'present')
    copy_item(value, exchanges, 'p', 'past')
    copy_item(value, exchanges, 'd', 'perfect')
    copy_item(value, exchanges, '3', 'third')
    copy_item(value, exchanges, '0', 'lemma')

    return value


def insert_dict(cursor: Cursor, value: dict):
    '''向表中插入字典'''
    keys, values = zip(*value.items())
    cursor.execute(
        'INSERT INTO ecdict (%s) VALUES (%s);' % (
            ', '.join(keys),
            ', '.join(('?',) * len(value))  # 生成对应数量的问号
        ),
        values
    )


def main():
    '''入口点'''
    file_name_in = input('输入(ultimate.csv): ')
    if not exists(file_name_in):
        print('输入文件不存在。')
        return
    with open(file_name_in, 'r', encoding='utf8', newline='') as file_in:
        csv_in = DictReader(file_in)
        file_name_out = input('输出: ')
        if exists(file_name_out):
            if input('输出文件已存在，覆盖？(y/n): ') == 'y':
                remove(file_name_out)
            else:
                return

        print('正在写入内存... ')
        with connect(':memory:', isolation_level=None) as conn_out:
            cursor_out = conn_out.cursor()
            cursor_out.execute('ATTACH DATABASE ? AS disk', (file_name_out,))
            create_table(cursor_out)
            time_start = time()
            for i, row in enumerate(csv_in, 1):
                # if ' ' in row['word']:  # 跳过词组
                #     continue
                value = row2dict(row)
                if i % 2000 == 0:
                    iw = i / 10000  # 已处理的单词数（万）
                    dt = time() - time_start  # 用时（秒）
                    v = iw / dt  # 速度（万每秒）
                    print('%-150s' % (
                        '已处理 %.1f 万词条，用时 %.2f 秒，'
                        '%.2f 万每秒，剩余 %.2f 秒'
                        % (iw, dt, v, (432.5 - iw) / v)
                    ), end='\r')
                insert_dict(cursor_out, value)

            print('\n正在写入磁盘... ', end='')
            time_start = time()
            cursor_out.execute(
                'CREATE TABLE disk.ecdict AS SELECT * FROM ecdict'
            )
            print('用时 %.2f 秒' % (time() - time_start))

    print('正在创建索引... ', end='')
    with connect(file_name_out, isolation_level=None) as conn:
        cursor = conn.cursor()
        time_start = time()
        cursor.execute(
            'CREATE INDEX word_nocase ON ecdict (word COLLATE NOCASE);'
        )
        print('用时 %.2f 秒' % (time() - time_start))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n已取消。')
    else:
        print('完成。')
