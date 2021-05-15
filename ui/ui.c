/**
 * 使用 MIT License 进行许可。
 * SPDX-License-Identifier: MIT
 * 版权所有 © 2020-2021 NKID00
 */

#define _GNU_SOURCE

#include <gpiod.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>

#include "g12864.h"

#define SCREEN_SID 23  // 物理编号 16
#define SCREEN_SCLK 24 // 物理编号 18
#define SCREEN_BLA 12  // 物理编号 32

#define dt_ms(t0, t1) (((t1).tv_sec - (t0).tv_sec) * 1000 + ((t1).tv_nsec - (t0).tv_nsec) / 1000000.0)

int main()
{
    g_info("加载字体");
    FILE *font_f = fopen("unifont.bin", "r");
    uint8_t *font = (uint8_t *)malloc(sizeof(uint8_t) * 16 * 16 * 65536 / 8);
    fread(font, sizeof(uint8_t), 16 * 16 * 65536 / 8, font_f);
    fclose(font_f);
    font_f = NULL;
    g_info_done();

    g_info("初始化屏幕");
    struct gpiod_chip *chip = gpiod_chip_open("/dev/gpiochip0");
    struct g_sc *sc = g_sc_create(gpiod_chip_get_line(chip, SCREEN_SID),
                                  gpiod_chip_get_line(chip, SCREEN_SCLK),
                                  gpiod_chip_get_line(chip, SCREEN_BLA));
    g_sc_set_bl(sc, G_BL_ON);
    g_info_done();

    g_info("强制刷新屏幕");
    g_sc_refresh_force(sc);
    g_info_done();

    struct g_fb *fb = g_sc_get_fb(sc);
    while (true)
    {
        g_fb_draw_text(fb, 0, 0, L"abcdefghijklmnop", true, font);
        g_sc_refresh(sc);
        g_fb_fill(fb, false);
        g_sc_refresh(sc);
    }

    g_sc_destroy(sc);
    gpiod_chip_close(chip);
    free(font);
}
