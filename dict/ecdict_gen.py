# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

'''转换 CSV 格式的 ECDICT 到 SQLite3 格式'''

from csv import DictReader
from sqlite3 import connect
from time import time

from util_gen import ask_input, ask_output, \
    copy_item, set_item, insert_dict, insert_info


def create_table(cursor, table: str):
    '''创建表'''
    cursor.execute(
        'CREATE TABLE %s (\n'
        '    word        TEXT PRIMARY KEY COLLATE NOCASE\n'
        '                NOT NULL UNIQUE,    -- 单词\n'
        '    phonetic    TEXT DEFAULT(NULL), -- 音标\n'
        '    pos         TEXT DEFAULT(NULL), -- 词性比率\n'
        '    definition  TEXT DEFAULT(NULL), -- 英文定义\n'
        '    translation TEXT DEFAULT(NULL), -- 中文翻译\n'
        '    collins     INTEGER DEFAULT(0), -- 柯林斯星级（0-5）\n'
        '    oxford      INTEGER DEFAULT(0), -- 牛津核心词汇（0-1）\n'
        '    gk          INTEGER DEFAULT(0), -- 高考范围（0-1）\n'
        '    cet4        INTEGER DEFAULT(0), -- 四级范围（0-1）\n'
        '    cet6        INTEGER DEFAULT(0), -- 六级范围（0-1）\n'
        '    ky          INTEGER DEFAULT(0), -- 考研范围（0-1）\n'
        '    plural      TEXT DEFAULT(NULL), -- 名词复数形式\n'
        '    comparative TEXT DEFAULT(NULL), -- 形容词比较级\n'
        '    superlative TEXT DEFAULT(NULL), -- 形容词最高级\n'
        '    present     TEXT DEFAULT(NULL), -- 动词现在分词\n'
        '    past        TEXT DEFAULT(NULL), -- 动词过去式\n'
        '    perfect     TEXT DEFAULT(NULL), -- 动词过去分词\n'
        '    third       TEXT DEFAULT(NULL), -- 动词第三人称单数\n'
        '    lemma       TEXT DEFAULT(NULL)  -- 词根\n'
        ');' % table
    )


def split_exchange(exchange: str) -> dict:
    '''分割词形变化表'''
    if exchange == '':
        return {}
    else:
        return dict(s.split(':') for s in exchange.split('/'))


def row2dict(row) -> dict:
    '''将 CSV 行转换为数据库行字典'''
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


def write_memory(c, csv_in):
    '''写入内存'''
    create_table(c, 'ecdict')
    time_temp = time_start = time()
    i = 0
    for row in csv_in:
        # if ' ' in row['word']:  # 跳过词组
        #     continue
        insert_dict(c, 'ecdict', row2dict(row))
        i += 1
        if i % 6000 == 0:
            iw = i / 10000  # 已处理的单词数（万）
            dt = time()  # 当前时间
            v = 0.6 / (dt - time_temp)  # 速度（万每秒）
            dt -= time_start  # 用时（秒）
            print('%-60s' % (
                '已处理 %.1f 万词条，用时 %.2f 秒，'
                '%.2f 万每秒，剩余 %.2f 秒'
                % (iw, dt, v, (432.5 - iw) / v)
            ), end='\r')
            time_temp = time()
    print()


def write_disk(c, file_name_out):
    '''写入磁盘'''
    c.execute('ATTACH DATABASE ? AS disk', (file_name_out,))
    create_table(c, 'disk.ecdict')
    c.execute('INSERT INTO disk.ecdict SELECT * FROM ecdict;')
    insert_info(c, 'disk.info', {
        'name':        'ECDICT',
        'description': 'Free English to Chinese Dictionary Database.',
        'link':        'https://github.com/skywind3000/ECDICT\n'
                       'https://github.com/skywind3000/ECDICT-ultimate',
        'version':     'Ultimate Database',
        'time':        1526439580,  # 2018-05-16T10:59:40Z
        'author':      'skywind3000',
        'license':     'MIT License',
        'program':     'ecdict.py'
    })


def main():
    '''入口点'''
    file_name_in = ask_input('ultimate.csv')
    if file_name_in is None:
        raise KeyboardInterrupt
    with open(file_name_in, 'r', encoding='utf8', newline='') as file_in:
        csv_in = DictReader(file_in)
        file_name_out = ask_output()
        if file_name_out is None:
            raise KeyboardInterrupt
        with connect(':memory:', isolation_level=None) as conn_out:
            c = conn_out.cursor()

            print('正在写入内存...')
            time_start = time()
            write_memory(c, csv_in)
            print('用时 %.2f 秒' % (time() - time_start))

            print('正在写入磁盘... ', end='')
            time_start = time()
            write_disk(c, file_name_out)
            print('用时 %.2f 秒' % (time() - time_start))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n已取消。')
    else:
        print('完成。')
