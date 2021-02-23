# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

class UI:  # 界面基类
    def __init__(self, screen):
        self._screen = screen

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
    def _(self, value):
        self._title = value
        self._screen.draw_text((0, 0), value)


class SettingsUI(MenuUI):  # 设置界面
    def __init__(self, screen):
        super().__init__(screen)


class AboutUI(MenuUI):  # 关于界面
    def __init__(self, screen):
        super().__init__(screen)


class DictionaryUI(UI):  # 辞典界面
    def __init__(self, screen):
        super().__init__(screen)
