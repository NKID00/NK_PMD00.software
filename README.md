## NK_PortableMultifunctionalDevice00

`便携多功能设备 00` 其实就是电子辞典。

市面上的电子辞典太贵还有平时用不到的多余功能，于是打算自己做一个。

这个项目大约从 2020 年 5 月就开始了，目前已经完成了约 10%。

此仓库为软件部分，硬件部分请前往 [NK_PMD00.hardware](https://github.com/NKID00/NK_PMD00.hardware)。

`ui/` 是用于显示和控制的前端部分。

- `ui/g12864.py` 用于和液晶显示器硬件交互。

- `ui/ui.py` 用于显示用户界面。

- `ui/unifont_gen.py` 用于转换 TrueType 格式的 Unifont 字体到能够读取的二进制点阵格式。

- 控制部分尚未编写。

`dict/` 是用于读取辞典数据库的后端部分。

- `dict/*_gen.py` 用于转换其他格式的辞典数据到能够读取的数据库格式。

`util/util.py` 是可能会使用的一些常用函数。

## 版权

版权所有 © 2020-2021 NKID00

使用 MIT License 进行许可。

使用 `dict/*_gen.py` 转换出的辞典数据库的版权归原辞典数据版权所有者所有，依照原辞典数据的许可证进行许可。

使用 `ui/unifont_gen.py` 转换出的二进制点阵格式的 Unifont 字体的版权归原 Unifont 字体版权所有者所有，依照原 Unifont 字体的 SIL Open Font License 1.1 许可证进行许可。
