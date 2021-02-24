# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

from collections import OrderedDict
from time import time_ns

from g12864 import TextFrame, Screen

# 导入 ../dict/ecdict.py 里的函数
from importlib.util import spec_from_file_location, module_from_spec
_ecdict_spec = spec_from_file_location('ecdict', '../dict/ecdict.py')
_ecdict = module_from_spec(_ecdict_spec)
_ecdict_spec.loader.exec_module(_ecdict)
# 用 globals() 批量赋值的话错误检查程序就不高兴了
ECDict = _ecdict.ECDict

EVENT_UP = 'up'
EVENT_DOWN = 'do'
EVENT_LEFT = 'le'
EVENT_RIGHT = 'ri'
EVENT_BACKSPACE = 'ba'


def word_warp(s: str, width: int = 16):
    warped = ''
    x = 0
    for c in s:
        if c == '\n':
            warped += c
            x = 0
        elif ord(c) < 128:  # ASCII
            if x == width:
                warped += '\n'
                x = 0
            x += 1
            warped += c
        else:  # Unicode
            if x >= width - 1:
                warped += '\n'
                x = 0
            x += 2
            warped += c
    return warped


class UI:
    '''界面基类'''

    def __init__(self, frame):
        self._frame = frame

    def process(self, event):
        '''处理事件'''
        pass

    def refresh(self):
        '''刷新界面'''
        pass


class MenuUI(UI):
    '''菜单界面'''

    def __init__(self, frame):
        super().__init__(frame)
        self._title = ''
        self._items = []
        self._select_index = 0
        self._invert_selected = True
        self._invert_title = False
        self.refresh()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if self._title != value:
            self._title = value
            self.refresh()

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, value):
        self._items = value
        if self._select_index >= len(value):
            self._select_index = len(value) - 1
        self.refresh()

    @property
    def select_index(self):
        return self._select_index

    @select_index.setter
    def select_index(self, value):
        if self._select_index != value:
            self._select_index = value
            self.refresh()

    @property
    def invert_selected(self):
        '''反转显示选中项'''
        return self._invert_selected

    @invert_selected.setter
    def invert_selected(self, value):
        if self._invert_selected != value:
            self._invert_selected = value
            self.refresh()

    @property
    def invert_title(self):
        '''反转显示标题'''
        return self._invert_title

    @invert_title.setter
    def invert_title(self, value):
        if self._invert_title != value:
            self._invert_title = value
            self.refresh()

    def process(self, event):
        '''处理事件'''
        if len(self.items) < 2:
            return
        if event == EVENT_UP:
            if self.select_index == 0:
                self.select_index = len(self.items) - 1
            else:
                self.select_index -= 1
        elif event == EVENT_DOWN:
            if self.select_index == len(self.items) - 1:
                self.select_index = 0
            else:
                self.select_index += 1

    def _refresh_0(self):
        self._frame.draw_text(0, 16, '(None)', True)

    def _refresh_1(self):
        if self.invert_selected:
            self._frame.draw_rectangle(0, 16, 127, 31, True)
        self._frame.draw_text(
            0, 16,
            self.items[0],
            not self.invert_selected
        )

    def _refresh_first(self):
        if self.invert_selected:
            self._frame.draw_rectangle(0, 16, 127, 31, True)
        self._frame.draw_text(
            0, 16,
            self.items[0],
            not self.invert_selected
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
        if self.invert_selected:
            self._frame.draw_rectangle(0, 32, 127, 47, True)
        self._frame.draw_text(
            0, 32,
            self.items[self.select_index],
            not self.invert_selected
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
        if self.invert_selected:
            self._frame.draw_rectangle(
                0, (i + 1) * 16,
                127, (i + 2) * 16 - 1,
                True
            )
        self._frame.draw_text(
            0, (i + 1) * 16,
            self.items[self.select_index],
            not self.invert_selected
        )

    def refresh(self):
        '''刷新界面'''
        self._frame.fill(False)
        if self.invert_title:
            self._frame.draw_rectangle(
                0, 0,
                127, 15,
                True
            )
        self._frame.draw_text(0, 0, self.title, not self.invert_title)
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


class DictionaryUI(MenuUI):
    '''辞典界面'''

    def __init__(self, frame, dictionary):
        super().__init__(frame)
        self._dictionary = dictionary
        self._select_index_word = 0
        self._word = ''
        self._title = '|'
        self._display_information = False  # 显示释义

    @property
    def word(self):
        return self._word

    @word.setter
    def word(self, value):
        if self._word != value:
            self._word = value
            self._title = value + '|'
            self._select_index = 0
            self._update_items_words()

    @property
    def display_information(self):
        return self._display_information

    @display_information.setter
    def display_information(self, value):
        if self._display_information != value:
            self._display_information = value
            if value:
                self._select_index_word = self._select_index
                self._title = self._word
                self._invert_selected = False
                self._update_items_information()
            else:
                self._select_index = self._select_index_word
                self._title = self._word + '|'
                self._invert_selected = True
                self._update_items_words()

    def _update_items_words(self):
        if self.word == '':
            self.items = []
        else:
            self.items = self._dictionary[self._word, 10]

    @staticmethod
    def _update_dict(d, key, s):
        d[key] = s if d[key] else ''

    @staticmethod
    def _format_dict(d, key, format_str):
        d[key] = (format_str % d[key]) if d[key] else ''

    def _update_items_information(self):
        info = self._dictionary[self.items[self.select_index]]

        self._format_dict(info, 'phonetic', '[%s]\n')

        self._format_dict(info, 'collins', 'C%d ')
        self._update_dict(info, 'oxford', 'OX ')
        self._update_dict(info, 'gk', '高 ')
        self._update_dict(info, 'cet4', '4 ')
        self._update_dict(info, 'cet6', '6 ')
        self._update_dict(info, 'ky', '研 ')

        self._format_dict(info, 'pos', '%s\n')

        self._format_dict(info, 'plural', '复 %s\n')
        self._format_dict(info, 'comparative', '比 %s\n')
        self._format_dict(info, 'superlative', '最 %s\n')
        self._format_dict(info, 'present', '现 %s\n')
        self._format_dict(info, 'past', '过 %s\n')
        self._format_dict(info, 'perfect', '完 %s\n')
        self._format_dict(info, 'third', '三 %s\n')
        self._format_dict(info, 'lemma', '根 %s\n')

        self._format_dict(info, 'definition', '%s\n')

        self._select_index = 1

        items = word_warp(
            '{collins}{oxford}{gk}{cet4}{cet6}{ky}\n'
            '{phonetic}'
            '{translation}\n'
            '{pos}'
            '{plural}'
            '{comparative}{superlative}'
            '{present}{past}{perfect}{third}'
            '{lemma}'
            '{definition}'.format(**info).replace('\n\n', '\n')
        ).splitlines(False)

        if items[0] == '':
            self.items = items[1:]
        else:
            self.items = items

    def process(self, event):
        '''处理事件'''
        if self.display_information:
            if len(self.items) < 4:
                return
            if event == EVENT_UP:
                if self.select_index == 1:
                    self.select_index = len(self.items) - 2
                else:
                    self.select_index -= 1
            elif event == EVENT_DOWN:
                if self.select_index >= len(self.items) - 2:
                    self.select_index = 1
                else:
                    self.select_index += 1
            elif event_is_left_or_backspace(event):
                self.display_information = False
        else:
            super().process(event)
            if event == EVENT_BACKSPACE:
                self.word = self.word[:-1]
            elif len(event) == 1 and event.isalpha:
                self.word += event.lower()
            elif event == EVENT_RIGHT:
                self.display_information = True


class SettingsUI(MenuUI):
    '''设置界面'''

    def __init__(self, frame, settings=None):
        super().__init__(frame)
        if settings is not None:
            self._settings = OrderedDict(settings)
            self._rebuild_items()
        else:
            self._settings = OrderedDict()

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        if self._settings != value:
            self._settings = value
            self._rebuild_items()

    def __getitem__(self, key):
        return self._settings[key]

    def __setitem__(self, key, value):
        self._settings[key] = value
        self._rebuild_items()

    def _rebuild_items(self):
        items = []
        for k, v in self.settings.items():
            if v:
                items.append('+ %s' % k)
            else:
                items.append('  %s' % k)
        self.items = items
    
    def process(self, event):
        '''处理事件'''
        super().process(event)
        if event == EVENT_RIGHT:
            k, v = tuple(self.settings.items())[self.select_index]
            self[k] = not v


class AboutUI(MenuUI):
    '''关于界面'''

    def __init__(self, frame):
        super().__init__(frame)
        self._select_index = 1
        self.invert_selected = False
        self.invert_title = True

    def process(self, event):
        '''处理事件'''
        if len(self.items) < 4:
            return
        if event == EVENT_UP:
            if self.select_index == 1:
                self.select_index = len(self.items) - 2
            else:
                self.select_index -= 1
        elif event == EVENT_DOWN:
            if self.select_index >= len(self.items) - 2:
                self.select_index = 1
            else:
                self.select_index += 1


latest_event = None


def get_event():
    global latest_event
    event = input('(NK_PMD00) ')
    if event.startswith('h') or event.startswith('?'):
        print(
            'help:\n'
            'up - up\n'
            'do - down\n'
            'le - left\n'
            'ri - right\n'
            '<letter> - letter\n'
        )
        return None
    elif event == '':
        event = latest_event
    else:
        latest_event = event
    return event


def event_is_left_or_backspace(event):
    return event == EVENT_LEFT or event == EVENT_BACKSPACE


def init():
    print('读取点阵格式的 Unifont 字体... ', end='', flush=True)
    time_start = time_ns()
    with open('unifont.bin', 'rb') as f:
        font_bitmap = f.read()
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('初始化屏幕... ', end='', flush=True)
    time_start = time_ns()
    screen = Screen(
        pin_sid=16,
        pin_sclk=18,
        pin_bla=32,
        initial_frame=TextFrame(font_bitmap)
    )
    screen.bl_value = 100
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('初始化菜单界面... ', end='', flush=True)
    time_start = time_ns()
    menu = MenuUI(screen.frame)
    menu.title = 'NK_PMD00  :P'
    menu.items = [
        # 234567890123456| <- 屏幕显示范围
        '辞典 Dictionary',
        '设置 Settings',
        '关于 About'
    ]
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('初始化设置界面... ', end='', flush=True)
    time_start = time_ns()
    settings = SettingsUI(screen.frame, (
        ('词组', True),
        ('柯林斯 0 星', True),
        ('缩写 abbr.', False),
        ('[网络]', False),
        ('[地名]', False),
        ('[医]', False),
        ('[药]', False),
        ('[化]', False),
        ('包含括号', False)
    ))
    settings.title = '设置 Settings'
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('初始化辞典界面... ', end='', flush=True)
    time_start = time_ns()
    dictionary = DictionaryUI(
        screen.frame,
        ECDict('../dict/ecdict.db', settings.settings)
    )
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('初始化关于界面... ', end='', flush=True)
    time_start = time_ns()
    about = AboutUI(screen.frame)
    about.title = '关于 About'
    about.items = (
        # 234567890123456| <- 屏幕显示范围
        'NK_便携多功能设\n'
        '备 00\n\n'
        '版权所有 2020-\n'
        '2021 NKID00\n\n'
        '使用 MIT Licens-\n'
        'e 进行许可。\n\n'
        '详情请见 https:/\n'
        '/github.com/NKID\n'
        '00/NK_PMD00.soft\n'
        'ware 和 https://\n'
        'github.com/NKID0\n'
        '0/NK_PMD00.hardw\n'
        'are\n\n'
        # 234567890123456| <- 屏幕显示范围
        'NK_PortableMultifunctionalDevice00\n\n'
        'Copyright 2020-\n'
        '2021 NKID00\n\n'
        'Under MIT Licen-\n'
        'se.\n\n'
        'See https://gith\n'
        'ub.com/NKID00/NK\n'
        '_PMD00.software\n'
        'and https://gith\n'
        'ub.com/NKID00/NK\n'
        '_PMD00.hardware\n'
        'for further inf-\n'
        'ormation.\n'
        # 234567890123456| <- 屏幕显示范围
    ).splitlines(False)
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('强制刷新屏幕... ', end='', flush=True)
    time_start = time_ns()
    menu.refresh()
    screen.refresh_force()
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    return screen, menu, dictionary, settings, about


def main():
    print('启动。', flush=True)
    time_start = time_ns()
    screen, menu, dictionary, settings, about = init()
    status = 'menu'
    print('初始化用时 %.3f 毫秒。' % ((time_ns() - time_start) / 1000000))

    print('进入主循环。', flush=True)
    while True:
        event = get_event()
        time_start = time_ns()
        if event is None or event == '':
            continue
        if status == 'menu':
            if event == EVENT_RIGHT:
                if menu.select_index == 0:  # Dictionary
                    dictionary.word = ''
                    dictionary.refresh()
                    status = 'dictionary'
                elif menu.select_index == 1:  # Settings
                    settings.refresh()
                    status = 'settings'
                else:  # About
                    about.refresh()
                    status = 'about'
            else:
                menu.process(event)
        elif status == 'dictionary':
            if event == EVENT_LEFT:
                if dictionary.display_information:
                    dictionary.process(event)
                else:
                    menu.refresh()
                    status = 'menu'
            else:
                dictionary.process(event)
        elif status == 'settings':
            if event_is_left_or_backspace(event):
                menu.refresh()
                status = 'menu'
            else:
                settings.process(event)
        elif status == 'about':
            if event_is_left_or_backspace(event):
                menu.refresh()
                status = 'menu'
            else:
                about.process(event)
        screen.refresh()
        print('用时 %.3f 毫秒。' % ((time_ns() - time_start) / 1000000))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('已退出。', flush=True)
