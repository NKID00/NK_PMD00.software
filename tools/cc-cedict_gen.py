# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

'''转换 ts 格式的 CC-CEDICT 到 SQLite3 格式'''

from re import match
from sqlite3 import connect, Cursor
from time import time

from util import ask_input, ask_output, insert_dict = _util.insert_dict, insert_info


def read_lines_iter(file):
    line = file.readline()
    while line != '':
        yield line
        line = file.readline()


def create_table(cursor: Cursor, table: str):
    '''创建表'''
    cursor.execute(
        'CREATE TABLE %s (\n'
        '    word        TEXT PRIMARY KEY NOT NULL -- 简体中文词语\n'
        '    phonetic    TEXT NOT NULL, -- 拼音\n'
        '    translation TEXT NOT NULL, -- 英文翻译\n'
        '    PRIMARY KEY (word, phonetic) -- 主键\n'
        ');' % table
    )


def line2dict(line) -> dict:
    '''将 CSV 行转换为数据库行字典'''
    value = {}

    match(r'\n', line)

    return value


def write_memory(c, file_in):
    '''写入内存'''
    create_table(c, 'cc-cedict')
    time_temp = time_start = time()
    i = 0
    for line in read_lines_iter(file_in):
        if line[0] == '#':
            if line[1] == '!':
                if line.startswith('#! version='):
                    info_version = int(line[11:-1])
                elif line.startswith('#! subversion='):
                    info_subversion = int(line[14:-1])
                elif line.startswith('#! time='):
                    info_time = int(line[8:-1])
            continue
        insert_dict(c, 'cc-cedict', line2dict(line))
        i += 1
        if i % 300 == 0:
            iw = i / 10000  # 已处理的单词数（万）
            dt = time()  # 当前时间
            v = 0.3 / (dt - time_temp)  # 速度（万每秒）
            dt -= time_start  # 用时（秒）
            print('%-60s' % (
                '已处理 %.2f 万词条，用时 %.2f 秒，'
                '%.2f 万每秒，剩余 %.2f 秒'
                % (iw, dt, v, (12 - iw) / v)
            ), end='\r')
            time_temp = time()
    print()
    return info_version, info_subversion, info_time


def write_disk(c, file_name_out, info_version, info_subversion, info_time):
    '''写入磁盘'''
    c.execute('ATTACH DATABASE ? AS disk', (file_name_out,))
    create_table(c, 'disk.cc-cedict')
    c.execute('INSERT INTO disk.cc-cedict SELECT * FROM cc-cedict;')
    insert_info(c, 'disk.info', {
        'name':        'CC-CEDICT',
        'description': 'Community maintained free Chinese-English dictionary.',
        'link':        'https://cc-cedict.org/wiki/',
        'version':     '%s.%s' % (info_version, info_subversion),
        'time':        info_time,
        'author':      'MDBG',
        'license':     'CC-BY-SA 4.0',
        'program':     'cc-cedict.py'
    })


def main():
    '''入口点'''
    file_name_in = ask_input('cedict_ts.u8')
    if file_name_in is None:
        raise KeyboardInterrupt
    with open(file_name_in, 'r', encoding='utf8') as file_in:
        file_name_out = ask_output()
        if file_name_out is None:
            raise KeyboardInterrupt
        with connect(':memory:', isolation_level=None) as conn_out:
            c = conn_out.cursor()

            print('正在写入内存...')
            time_start = time()
            info_version, info_subversion, info_time = write_memory(c, file_in)
            print('用时 %.2f 秒' % (time() - time_start))

            print('正在写入磁盘... ', end='')
            time_start = time()
            write_disk(
                c, file_name_out, info_version, info_subversion, info_time
            )
            print('用时 %.2f 秒' % (time() - time_start))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n已取消。')
    else:
        print('完成。')
