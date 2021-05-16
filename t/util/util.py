# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

'''可能会使用的一些常用函数'''

__all__ = (
    'ask_input', 'ask_output', 'copy_item', 'set_item',
    'insert_dict', 'insert_info', 'group_iter',
)

from os.path import exists
from os import remove


def ask_input(hint=None):
    file = input(('输入(%s): ' % hint) if hint is not None else '输入: ')
    if not exists(file):
        print('输入文件不存在。')
        return None
    return file


def ask_output():
    file = input('输出: ')
    if exists(file):
        if input('输出文件已存在，覆盖？(y/n): ') == 'y':
            remove(file)
        else:
            return None
    return file


def copy_item(
    target: dict, source: dict, key, target_key=None,
    default=None, factory=None, replace_newline: bool = False
):
    '''如果不是空的就复制'''
    if target_key is None:
        target_key = key
    if key in source and source[key] != '':
        if replace_newline:
            if factory is not None:
                target[target_key] = factory(source[key].replace('\\n', '\n'))
            else:
                target[target_key] = source[key].replace('\\n', '\n')
        else:
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


def insert_dict(cursor, table: str, value: dict):
    '''向表中插入字典'''
    keys, values = zip(*value.items())
    cursor.execute(
        'INSERT INTO %s (%s) VALUES (%s);' % (
            table,
            ', '.join(keys),
            ', '.join(('?',) * len(value))  # 生成对应数量的问号
        ),
        values
    )


def insert_info(cursor, table: str, info: dict):
    '''新建信息表并插入信息'''
    cursor.execute(
        'CREATE TABLE %s (\n'
        '    name        TEXT,    -- 名称\n'
        '    description TEXT,    -- 描述\n'
        '    link        TEXT,    -- 链接\n'
        '    version     TEXT,    -- 版本\n'
        '    time        INTEGER, -- 发布时间（Unix 时间）\n'
        '    author      TEXT,    -- 作者或发布者\n'
        '    license     TEXT,    -- 许可证\n'
        '    program     TEXT     -- 用来读取数据的程序名\n'
        ');' % table
    )
    insert_dict(cursor, table, info)


def group_iter(it, n):
    '''依次将迭代器产出的值分组，每组 n 个，产出这些组'''
    it = iter(it)
    while True:
        g = []
        try:
            for _ in range(n):
                g.append(next(it))
        except StopIteration:
            if len(g) > 0:
                yield tuple(g)
            return
        else:
            yield tuple(g)
