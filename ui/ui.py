# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

from time import time_ns

from g12864 import TextFrame, Screen

EVENT_KEY_UP = 'up'
EVENT_KEY_DOWN = 'do'
EVENT_KEY_LEFT = 'le'
EVENT_KEY_RIGHT = 'ri'


class UI:  # 界面基类
    def __init__(self, screen):
        self._screen = screen

    def process(self, event):
        pass

    def refresh(self):
        self._screen.refresh()


class MenuUI(UI):  # 菜单界面
    def __init__(self, screen):
        super().__init__(screen)
        self._title = ''

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self._screen.frame.draw_text(0, 0, value)

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, value):
        self._items = value
        self._screen.frame.draw_text(0, 0, value)


class SettingsUI(MenuUI):  # 设置界面
    def __init__(self, screen):
        super().__init__(screen)


class AboutUI(MenuUI):  # 关于界面
    def __init__(self, screen):
        super().__init__(screen)


class DictionaryUI(UI):  # 辞典界面
    def __init__(self, screen):
        super().__init__(screen)


def main():
    print('读取二进制点阵格式的 Unifont 字体... ', end='', flush=True)
    time_start = time_ns()
    with open('unifont.bin', 'rb') as f:
        font_bitmap = f.read()
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('创建屏幕实例并初始化... ', end='', flush=True)
    time_start = time_ns()
    screen = Screen(
        pin_sid=16,
        pin_sclk=18,
        pin_bla=32,
        initial_frame=TextFrame(font_bitmap)
    )
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    menu = MenuUI(screen)
    menu.


if __name__ == '__main__':
    main()
