/**
 * 使用 MIT License 进行许可。
 * SPDX-License-Identifier: MIT
 * 版权所有 © 2020-2021 NKID00
 */

#include "ui.hpp"

#ifndef NK_PMD00_VERSION
#define NK_PMD00_VERSION "未知"
#endif
#ifndef NK_PMD00_COMMIT
#define NK_PMD00_COMMIT "未知"
#endif
#ifndef NK_PMD00_BUILD
#define NK_PMD00_BUILD "未知"
#endif

int main()
{
    std::cout << "NK_PMD00"
              << "\n版本 " << NK_PMD00_VERSION << " (" << NK_PMD00_COMMIT << ")"
              << "\n构建时间 " << NK_PMD00_BUILD
#ifdef DEBUG
              << "\n调试模式 "
              << "c++ " << __cplusplus
              << ", posix " << _POSIX_VERSION
              << ", unix " << _XOPEN_VERSION
              << ", gcc " << __GNUC__ << "." << __GNUC_MINOR__ << "." << __GNUC_PATCHLEVEL__
#endif
              << "\n版权所有 © 2020-2021 NKID00\n使用 MIT License 进行许可\n"
              << std::endl;

    g_info("载入字体");
    auto font_f = std::fopen("unifont.bin", "r");
    font = reinterpret_cast<std::uint8_t *>(std::malloc(sizeof(uint8_t) * 16 * 16 * 65536 / 8));
    std::fread(font, sizeof(uint8_t), 16 * 16 * 65536 / 8, font_f);
    std::fclose(font_f);
    font_f = nullptr;
    g_info_done();

    g_info("初始化屏幕");
    auto chip = gpiod_chip_open("/dev/gpiochip0");
    auto sc = g_sc_create(gpiod_chip_get_line(chip, SCREEN_SID),
                          gpiod_chip_get_line(chip, SCREEN_SCLK),
                          gpiod_chip_get_line(chip, SCREEN_BLA));
    g_sc_set_bl(sc, G_BL_ON);
    g_info_done();

    g_info("初始化键盘");
    auto row0 = gpiod_chip_get_line(chip, K_ROW0);
    auto row1 = gpiod_chip_get_line(chip, K_ROW1);
    auto row2 = gpiod_chip_get_line(chip, K_ROW2);
    auto row3 = gpiod_chip_get_line(chip, K_ROW3);
    gpiod_line_request_output(row0, K_CONSUMER, K_LOW);
    gpiod_line_request_output(row1, K_CONSUMER, K_LOW);
    gpiod_line_request_output(row2, K_CONSUMER, K_LOW);
    gpiod_line_request_output(row3, K_CONSUMER, K_LOW);
    auto col0 = gpiod_chip_get_line(chip, K_COL0);
    auto col1 = gpiod_chip_get_line(chip, K_COL1);
    auto col2 = gpiod_chip_get_line(chip, K_COL2);
    auto col3 = gpiod_chip_get_line(chip, K_COL3);
    gpiod_line_request_input(row0, K_CONSUMER);
    gpiod_line_request_input(row1, K_CONSUMER);
    gpiod_line_request_input(row2, K_CONSUMER);
    gpiod_line_request_input(row3, K_CONSUMER);
    g_info_done();

    g_info("初始化其他杂项");
    auto fb = g_sc_get_fb(sc);
    auto ui = DictionaryUI(fb, "dict/ecdict.db");
    static struct timespec t = {.tv_sec = 0, .tv_nsec = 5000000};
    g_info_done();

    g_info("强制刷新屏幕");
    ui.refresh();
    g_sc_refresh_force(sc);
    g_info_done();

    g_info("进入主循环") << std::endl;
    ui.t();
    g_sc_refresh(sc);

    while (true)
    {
        g_info("等待事件");
        auto event = Event::None;
        while (true)
        {
            nanosleep(&t, nullptr);
        }
        g_info_done();
        g_info("处理事件");
        ui.process(event);
        g_info_done();
        g_info("刷新屏幕");
        g_sc_refresh(sc);
        g_info_done();
    }

    // 永远不会运行到这里

    /*
    g_sc_destroy(sc);
    gpiod_chip_close(chip);
    std::free(font);
    */
}
