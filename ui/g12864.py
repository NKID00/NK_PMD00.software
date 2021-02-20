# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

__all__ = ('SCREEN_WIDTH', 'SCREEN_HEIGHT', 'SCREEN_PIXELS', 'SCREEN_X_BYTES',
           'SCREEN_BYTES', 'Frame', 'Screen')

from typing import Optional

# 常量
SCREEN_WIDTH, SCREEN_HEIGHT = 128, 64  # SCREEN_WIDTH 必须是 8 的整数倍
SCREEN_PIXELS = SCREEN_WIDTH * SCREEN_HEIGHT
SCREEN_X_BYTES = SCREEN_WIDTH // 8
SCREEN_BYTES = SCREEN_X_BYTES * SCREEN_HEIGHT


class Frame:
    '''帧画面缓存'''

    def __init__(self, source: Optional = None):
        self._data = bytearray(SCREEN_BYTES)

    @staticmethod
    def point2index(x: int, y: int) -> int:
        return x // 8 + y * SCREEN_X_BYTES

    def get_byte(self, x: int, y: int) -> int:
        return self._data[self.point2index(x, y)]

    def set_byte(self, x: int, y: int, value: int):
        self._data[self.point2index(x, y)] = value

    def get_pixel(self, x: int, y: int) -> bool:
        return self.get_byte(x, y) & (1 << (x % 8)) != 0

    def set_pixel(self, x: int, y: int, value: bool):
        if value:
            self.set_byte(x, y, self.get_byte(x, y) | (1 << (x % 8)) != 0)
        else:
            self.set_byte(x, y, self.get_byte(x, y) & ~(1 << (x % 8)) != 0)


class Screen:
    '''屏幕'''

    def __init__(self):
        self.frame = Frame()
