# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

'''转换 TrueType 格式的 Unifont 字体到二进制点阵格式'''

from freetype import Face
from time import time

# 导入 ../util/util.py 里的函数
from importlib.util import spec_from_file_location, module_from_spec
_util_spec = spec_from_file_location('util', '../util/util.py')
_util = module_from_spec(_util_spec)
_util_spec.loader.exec_module(_util)
# 用 globals() 批量赋值的话错误检查程序就不高兴了
ask_input = _util.ask_input
ask_output = _util.ask_output
group_iter = _util.group_iter


def convert_char(face, char):
    '''将单个字符转换为二进制点阵格式'''
    # 加载点阵
    face.load_char(char)
    width = face.glyph.bitmap.width
    height = face.glyph.bitmap.rows
    left = face.glyph.bitmap_left
    top = face.glyph.bitmap_top

    if width == 0 or left < 0:
        return b'\x00' * (16 * 16 // 8)

    bitmap = ''.join(map(
        lambda x: '1' if x else '0',
        face.glyph.bitmap.buffer
    ))

    # 计算补充的 0
    zeros_top = '0' * 16 * (16 - 2 - top)
    zeros_bottom = '0' * 16 * (2 + top - height)
    zeros_left = '0' * left
    zeros_right = '0' * (16 - left - width)

    # 将点阵转换为二进制字面值
    buffer = zeros_top
    for y in range(height):
        buffer += zeros_left
        for x in range(width):
            buffer += bitmap[y * width + x]
        buffer += zeros_right
    buffer += zeros_bottom

    # 将二进制字面值按字节分组，转换为数字，再转换为字节串
    return bytes(map(
        lambda x: int(''.join(x), base=2),
        group_iter(buffer, 8)
    ))


def main():
    '''入口点'''
    ttf_in = ask_input('unifont-*.ttf')
    if ttf_in is None:
        raise KeyboardInterrupt
    face = Face(ttf_in)
    face.set_char_size(16 * 64)
    file_name_out = ask_output()
    if file_name_out is None:
        raise KeyboardInterrupt
    buffer = bytearray()

    print('正在写入内存... ', flush=True)
    time_start = time()
    for char in range(65536):
        print('Unicode:', char, end='\r', flush=True)
        b = convert_char(face, char)
        if len(b) != 16 * 16 // 8:
            raise RuntimeError(char, chr(char))
        buffer += b
    print('\n用时 %.2f 秒' % (time() - time_start))

    print('正在写入磁盘... ', end='', flush=True)
    time_start = time()
    with open(file_name_out, 'wb') as f:
        f.write(buffer)
    print('用时 %.2f 秒' % (time() - time_start))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n已取消。', flush=True)
    else:
        print('完成。', flush=True)
