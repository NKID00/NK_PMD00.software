## NK_PortableMultifunctionalDevice00

`便携多功能设备 00` 其实就是电子辞典。

市面上的电子辞典太贵还有平时用不到的多余功能，于是打算自己做一个。

这个项目大约从 2020 年 5 月就开始了，目前软件部分已经完成了约 70%。

此仓库为软件部分，硬件部分请前往 [NK_PMD00.hardware](https://github.com/NKID00/NK_PMD00.hardware)。

## 代码用途

`src/` 是运行在便携多功能设备 00 上的程序。

- `src/ui/` 是用于显示和控制的前端部分。

  - `src/ui/g12864/` 是用于和液晶显示器硬件交互的 [g12864](https://github.com/NKID00/g12864) 库。

  - `src/ui/ui.cpp` 用于显示用户界面。

  - 控制部分尚未编写。

- `src/dict/` 是用于读取辞典数据库的后端部分。

`tools/` 是用于转换各种格式的数据到适合读取的格式的工具。

- `tools/*dict_gen.py` 用于转换其他格式的辞典数据到适合读取的数据库格式。

- `tools/unifont_gen.py` 用于转换 TrueType 格式的 Unifont 字体到适合读取的点阵格式。

- `tools/util.py` 是可能会使用的一些常用函数。

## 构建

```sh
$ sudo apt install tcl # sqlite3 编译时依赖
$ git clone https://github.com/NKID00/NK_PMD00.software.git
$ cd NK_PMD00.software
$ git submodule update --init # 这一步需要下载约 200 MB 的数据
$ make run
```

## 版权

版权所有 © 2020-2021 NKID00

使用 MIT License 进行许可。

使用 `tools/*_gen.py` 转换出的数据的版权归原数据版权所有者所有，依照原数据的许可证进行许可。

- 使用 `tools/ecdict_gen.py` 转换出的 SQLite3 格式的 ECDICT 的版权归原 ECDICT 版权所有者所有，依照原 ECDICT 的 MIT License 进行许可。ECDICT 相关链接：

  - https://github.com/skywind3000/ECDICT

  - https://github.com/skywind3000/ECDICT-ultimate

- 使用 `tools/unifont_gen.py` 转换出的点阵格式的 Unifont 字体的版权归原 Unifont 字体版权所有者所有，依照原 Unifont 字体的 SIL Open Font License 1.1 进行许可。Unifont 字体相关链接：

  - http://unifoundry.com/unifont/index.html
