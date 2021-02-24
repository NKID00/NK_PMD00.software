# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

from time import time_ns

from g12864 import TextFrame, Screen

EVENT_KEY_UP = 'up'
EVENT_KEY_DOWN = 'do'
EVENT_KEY_LEFT = 'le'
EVENT_KEY_RIGHT = 'ri'
EVENT_KEY_OK = 'ok'


class UI:
    '''界面基类'''

    def __init__(self, frame):
        self._frame = frame

    def process(self, event):
        pass

    def refresh(self):
        pass


class MenuUI(UI):
    '''菜单界面'''

    def __init__(self, frame):
        super().__init__(frame)
        self.title = ''
        self.items = []
        self.select_index = 0
        self.display_selected = True  # 突出显示选中项

    def process(self, event):
        if event == EVENT_KEY_UP:
            if self.select_index > 0:
                self.select_index -= 1
        elif event == EVENT_KEY_DOWN:
            if self.select_index < len(self.items):
                self.select_index += 1

    def _refresh_0(self):
        self._frame.draw_text(0, 16, '(None)', True)

    def _refresh_1(self):
        if self.display_selected:
            self._frame.draw_rectangle(0, 16, 127, 31, True)
        self._frame.draw_text(
            0, 16,
            self.items[0],
            not self.display_selected
        )

    def _refresh_first(self):
        if self.display_selected:
            self._frame.draw_rectangle(0, 16, 127, 31, True)
        self._frame.draw_text(
            0, 16,
            self.items[0],
            not self.display_selected
        )
        for i, item in enumerate(self.items[1:3], 2):
            self._frame.draw_text(
                0, i * 16,
                item,
                True
            )

    def _refresh_middle(self):
        self._frame.draw_text(
            0, 16,
            self.items[self.select_index - 1],
            True
        )
        if self.display_selected:
            self._frame.draw_rectangle(0, 32, 127, 47, True)
        self._frame.draw_text(
            0, 32,
            self.items[self.select_index],
            not self.display_selected
        )
        self._frame.draw_text(
            0, 48,
            self.items[self.select_index + 1],
            True
        )

    def _refresh_last(self):
        for i, item in enumerate(self.items[-3:-1], 1):
            self._frame.draw_text(
                0, i * 16,
                item,
                True
            )
        if self.display_selected:
            self._frame.draw_rectangle(
                0, (i + 1) * 16,
                127, (i + 2) * 16 - 1,
                True
            )
        self._frame.draw_text(
            0, (i + 1) * 16,
            self.items[self.select_index],
            not self.display_selected
        )

    def refresh(self):
        '''刷新菜单界面'''
        self._frame.fill(False)
        self._frame.draw_text(0, 0, self.title, True)
        if len(self.items) == 0:
            self._refresh_0()
        elif len(self.items) == 1:
            self._refresh_1()
        elif self.select_index == 0:  # 选中第一项
            self._refresh_first()
        elif self.select_index < len(self.items) - 1:  # 选中中间项
            self._refresh_middle()
        else:  # self.select_index == len(self.items) - 1  # 选中最后一项
            self._refresh_last()


class SettingsUI(MenuUI):
    '''设置界面'''

    def __init__(self, screen):
        super().__init__(screen)


class AboutUI(MenuUI):
    '''关于界面'''

    def __init__(self, screen):
        super().__init__(screen)
        self.display_selected = False


class DictionaryUI(UI):
    '''辞典界面'''

    def __init__(self, screen):
        super().__init__(screen)


def test():
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
    screen.bl_value = 100
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('清屏... ', end='', flush=True)
    time_start = time_ns()
    screen.refresh_force()
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('创建菜单界面实例并初始化... ', end='', flush=True)
    time_start = time_ns()
    menu = MenuUI(screen.frame)
    menu.title = 'Title!!!'
    menu.items = ['Item No. 1', 'Item No. 2', 'Item No. 3', 'Item No. 4']
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('刷新菜单界面... ', end='', flush=True)
    time_start = time_ns()
    menu.refresh()
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('刷新屏幕... ', end='', flush=True)
    time_start = time_ns()
    screen.refresh()
    input('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('选中第二项... ', end='', flush=True)
    time_start = time_ns()
    menu.process(EVENT_KEY_DOWN)
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('刷新菜单界面... ', end='', flush=True)
    time_start = time_ns()
    menu.refresh()
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('刷新屏幕... ', end='', flush=True)
    time_start = time_ns()
    screen.refresh()
    input('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('选中第三项... ', end='', flush=True)
    time_start = time_ns()
    menu.process(EVENT_KEY_DOWN)
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('刷新菜单界面... ', end='', flush=True)
    time_start = time_ns()
    menu.refresh()
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('刷新屏幕... ', end='', flush=True)
    time_start = time_ns()
    screen.refresh()
    input('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('选中第四项... ', end='', flush=True)
    time_start = time_ns()
    menu.process(EVENT_KEY_DOWN)
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('刷新菜单界面... ', end='', flush=True)
    time_start = time_ns()
    menu.refresh()
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('刷新屏幕... ', end='', flush=True)
    time_start = time_ns()
    screen.refresh()
    input('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))


if __name__ == '__main__':
    test()
