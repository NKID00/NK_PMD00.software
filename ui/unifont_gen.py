# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

'''转换 CSV 格式的 ECDICT 到 SQLite3 格式'''

from freetype import Face
from time import time

from importlib.util import spec_from_file_location, module_from_spec

# 强行导入隔壁 util_gen 里的函数
spec = spec_from_file_location('util_gen', '../dict/util_gen.py')
util_gen = module_from_spec(spec)
spec.loader.exec_module(util_gen)
ask_input, ask_output = util_gen.ask_input, util_gen.ask_output


def write_memory(ttf_in):
    '''写入内存'''
    data = bytearray()


def write_disk(data, file_name_out):
    '''写入磁盘'''
    pass


def group(it, n):
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


def main():
    '''入口点'''
    ttf_in = ask_input('unifont-*.ttf')
    if ttf_in is None:
        raise KeyboardInterrupt
    f = Face(ttf_in)
    f.set_char_size(16 * 64)
    file_name_out = ask_output()
    if file_name_out is None:
        raise KeyboardInterrupt
    for i in range(65536):
        f.load_char(i)
        print('\n'.join(map(
            lambda x: ''.join(x), group(map(
                lambda x: '##' if x else '  ', f.glyph.bitmap.buffer
            ), f.glyph.bitmap.width)
        )))
    # print('正在写入磁盘... ', end='')
    # time_start = time()
    # write_disk(c, file_name_out)
    # print('用时 %.2f 秒' % (time() - time_start))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n已取消。')
    else:
        print('完成。')
