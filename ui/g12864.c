/**
 * 使用 MIT License 进行许可。
 * SPDX-License-Identifier: MIT
 * 版权所有 © 2020-2021 NKID00
 */

#include "g12864.h"

#include <gpiod.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>

#define G_SCREEN_PIXELS G_SCREEN_WIDTH *G_SCREEN_HEIGHT
#define G_SCREEN_X_BYTES G_SCREEN_WIDTH / 8
#define G_SCREEN_BYTES G_SCREEN_X_BYTES *G_SCREEN_HEIGHT

#define G_LOW 0
#define G_HIGH 1

#define G_CONSUMER "g12864"

/* TODO: 没有检查 malloc 错误（虽然内存肯定够） */

struct g_fb
{
    uint8_t data[G_SCREEN_BYTES];
};

struct g_sc
{
    struct g_fb *fb, *current; // 双缓冲区
    struct gpiod_line *sid, *sclk, *bla;
};

struct g_fb *
g_fb_create()
{
    struct g_fb *fb = (struct g_fb *)malloc(sizeof(struct g_fb));
    g_fb_fill(fb, false);
    return fb;
}

void g_fb_destroy(struct g_fb *fb)
{
    free(fb);
}

uint8_t *
g_fb_get_byte(struct g_fb *fb, int x, int y)
{
    return fb->data + x / 8 + y * G_SCREEN_X_BYTES;
}

bool g_fb_get_pixel(struct g_fb *fb, int x, int y)
{
    return (*g_fb_get_byte(fb, x, y) & (0x80 /* 0b1000_0000 */ >> (x % 8))) != 0;
}

void g_fb_set_pixel(struct g_fb *fb, int x, int y, bool value)
{
    if (x >= G_SCREEN_WIDTH || y >= G_SCREEN_HEIGHT)
    {
        return;
    }

    if (value)
    {
        *g_fb_get_byte(fb, x, y) |= (0x80 /* 0b1000_0000 */ >> (x % 8));
    }
    else
    {
        *g_fb_get_byte(fb, x, y) &= ~(0x80 /* 0b1000_0000 */ >> (x % 8));
    }
}

struct g_fb *
g_fb_copy(struct g_fb *fb_src)
{
    struct g_fb *fb = g_fb_create();
    memcpy(fb->data, fb_src->data, sizeof(fb->data));
    return fb;
}

void g_fb_fill(struct g_fb *fb, bool value)
{
    if (value)
    {
        memset(fb->data, 0xff, sizeof(fb->data));
    }
    else
    {
        memset(fb->data, 0, sizeof(fb->data));
    }
}

void g_fb_draw_rect(struct g_fb *fb, int x0, int y0, int x1, int y1, bool value)
{
    if (x0 > x1)
    {
        int t = x0;
        x0 = x1;
        x1 = t;
    }
    if (y0 > y1)
    {
        int t = y0;
        y0 = y1;
        y1 = t;
    }

    for (int x = x0; x <= x1; x++)
    {
        for (int y = y0; y <= y1; y++)
        {
            g_fb_set_pixel(fb, x, y, value);
        }
    }
}

void g_fb_draw_char_ascii(struct g_fb *fb, int x, int y, wchar_t ch, bool value, uint8_t *font)
{
    int address = ch * 16 * 16 / 8;
    for (int dy = 0; dy < 16; dy++)
    {
        for (int dx = 0; dx < 8; dx++)
        {
            if (font[address + dy * 2] & (0x80 /* 0b1000_0000 */ >> dx))
            {
                g_fb_set_pixel(fb, x + dx, y + dy, value);
            }
        }
    }
}

void g_fb_draw_char_unicode(struct g_fb *fb, int x, int y, wchar_t ch, bool value, uint8_t *font)
{
    int address = ch * 16 * 16 / 8;
    for (int dy = 0; dy < 16; dy++)
    {
        for (int dx = 0; dx < 8; dx++)
        {
            if (font[address + dy * 2] & (0x80 /* 0b1000_0000 */ >> dx))
            {
                g_fb_set_pixel(fb, x + dx, y + dy, value);
            }
            if (font[address + dy * 2 + 1] & (0x80 /* 0b1000_0000 */ >> dx))
            {
                g_fb_set_pixel(fb, x + dx + 8, y + dy, value);
            }
        }
    }
}

void g_fb_draw_char(struct g_fb *fb, int x, int y, wchar_t ch, bool value, uint8_t *font)
{
    if (ch < 128)
    {
        g_fb_draw_char_ascii(fb, x, y, ch, value, font);
    }
    else
    {
        g_fb_draw_char_unicode(fb, x, y, ch, value, font);
    }
}

void g_fb_draw_text(struct g_fb *fb, int x, int y, wchar_t *text, bool value, uint8_t *font)
{
    int x0 = x;
    for (; *text != L'\0'; text++)
    {
        if (*text < 128)
        {
            if (*text == L'\n')
            {
                x = x0;
                y += 16;
                continue;
            }
            g_fb_draw_char_ascii(fb, x, y, *text, value, font);
            x += 8;
        }
        else
        {
            g_fb_draw_char_unicode(fb, x, y, *text, value, font);
            x += 16;
        }
    }
}

void g_delay()
{
    return;
}

struct g_sc *
g_sc_create(struct gpiod_line *sid,
            struct gpiod_line *sclk,
            struct gpiod_line *bla)
{
    struct g_sc *sc = (struct g_sc *)malloc(sizeof(struct g_sc));
    sc->fb = g_fb_create();
    sc->current = g_fb_create();
    sc->sid = sid;
    sc->sclk = sclk;
    sc->bla = bla;
    gpiod_line_request_output(sid, G_CONSUMER, G_LOW);
    gpiod_line_request_output(sclk, G_CONSUMER, G_LOW);
    gpiod_line_request_output(bla, G_CONSUMER, G_LOW);
    g_sc_write_setup(sc);
    return sc;
}

void g_sc_destroy(struct g_sc *sc)
{
    gpiod_line_release(sc->sid);
    gpiod_line_release(sc->sclk);
    gpiod_line_release(sc->bla);
    g_fb_destroy(sc->fb);
    g_fb_destroy(sc->current);
    free(sc);
}

struct g_fb *
g_sc_get_fb(struct g_sc *sc)
{
    return sc->fb;
}

void g_sc_set_bl(struct g_sc *sc, int value)
{
    gpiod_line_set_value(sc->bla, value);
}

void g_sc_write_bit_high(struct g_sc *sc)
{
    gpiod_line_set_value(sc->sid, G_HIGH);
    gpiod_line_set_value(sc->sclk, G_HIGH);
    g_delay();
    gpiod_line_set_value(sc->sclk, G_LOW);
}

void g_sc_write_bit_low(struct g_sc *sc)
{
    gpiod_line_set_value(sc->sid, G_LOW);
    gpiod_line_set_value(sc->sclk, G_HIGH);
    g_delay();
    gpiod_line_set_value(sc->sclk, G_LOW);
}

void g_sc_write_bit(struct g_sc *sc, int value)
{
    gpiod_line_set_value(sc->sid, value);
    gpiod_line_set_value(sc->sclk, G_HIGH);
    g_delay();
    gpiod_line_set_value(sc->sclk, G_LOW);
}

void g_sc_write_byte(struct g_sc *sc, int rs, uint8_t value)
{
    // 同步
    g_sc_write_bit_high(sc);
    g_sc_write_bit_high(sc);
    g_sc_write_bit_high(sc);
    g_sc_write_bit_high(sc);
    g_sc_write_bit_high(sc);

    // R/W
    g_sc_write_bit_low(sc);

    // RS
    g_sc_write_bit(sc, rs);

    // 间隔
    g_sc_write_bit_low(sc);

    // 高四位
    g_sc_write_bit(sc, value & 0x80 /* 0b1000_0000*/);
    g_sc_write_bit(sc, value & 0x40 /* 0b0100_0000*/);
    g_sc_write_bit(sc, value & 0x20 /* 0b0010_0000*/);
    g_sc_write_bit(sc, value & 0x10 /* 0b0001_0000*/);

    // 间隔
    g_sc_write_bit_low(sc);
    g_sc_write_bit_low(sc);
    g_sc_write_bit_low(sc);
    g_sc_write_bit_low(sc);

    // 低四位
    g_sc_write_bit(sc, value & 0x08 /* 0b0000_1000*/);
    g_sc_write_bit(sc, value & 0x04 /* 0b0000_0100*/);
    g_sc_write_bit(sc, value & 0x02 /* 0b0000_0010*/);
    g_sc_write_bit(sc, value & 0x01 /* 0b0000_0001*/);

    // 间隔
    g_sc_write_bit_low(sc);
    g_sc_write_bit_low(sc);
    g_sc_write_bit_low(sc);
    g_sc_write_bit_low(sc);
}

void g_sc_write_byte_command(struct g_sc *sc, uint8_t value)
{
    g_sc_write_byte(sc, G_LOW, value);
    g_delay();
}

void g_sc_write_byte_data(struct g_sc *sc, uint8_t value)
{
    g_sc_write_byte(sc, G_HIGH, value);
    g_delay();
}

void g_sc_write_setup(struct g_sc *sc)
{
    // 设置 8 位 MPU 接口，基本指令集
    g_sc_write_byte_command(sc, 0x30 /* 0b0011_0000 */);

    // 清除字符显示内存防止干扰绘图显示
    g_sc_write_byte_command(sc, 0x01 /* 0b0000_0001 */);
    struct timespec t;
    t.tv_sec = 0;
    t.tv_nsec = 1600000;
    nanosleep(&t, NULL);

    // 设置扩充指令集
    g_sc_write_byte_command(sc, 0x34 /* 0b0011_0100 */);

    // 设置绘图显示开
    g_sc_write_byte_command(sc, 0x36 /* 0b0011_0110 */);
}

void g_sc_write_address(struct g_sc *sc, int x, int y)
{
    g_sc_write_byte_command(sc, 0x80 /* 0b1000_0000 */ + y);
    g_sc_write_byte_command(sc, 0x80 /* 0b1000_0000 */ + x);
}

void g_sc_refresh(struct g_sc *sc)
{
    uint8_t *data = sc->fb->data;
    uint8_t *current = sc->current->data;

    // 上半屏幕
    for (int y = 0; y < G_SCREEN_HEIGHT / 2; y++)
    {
        for (int x = 0; x < G_SCREEN_X_BYTES; x += 2)
        {
            if (data[x + y * G_SCREEN_X_BYTES] != current[x + y * G_SCREEN_X_BYTES] || data[x + y * G_SCREEN_X_BYTES + 1] != current[x + y * G_SCREEN_X_BYTES + 1])
            {
                // 两数据字不同，写入
                g_sc_write_address(sc, x / 2, y);
                g_sc_write_byte_data(sc, data[x + y * G_SCREEN_X_BYTES]);
                g_sc_write_byte_data(sc, data[x + y * G_SCREEN_X_BYTES + 1]);
            }
        }
    }

    // 下半屏幕
    for (int y = G_SCREEN_HEIGHT / 2; y < G_SCREEN_HEIGHT; y++)
    {
        for (int x = 0; x < G_SCREEN_X_BYTES; x += 2)
        {
            if (data[x + y * G_SCREEN_X_BYTES] != current[x + y * G_SCREEN_X_BYTES] || data[x + y * G_SCREEN_X_BYTES + 1] != current[x + y * G_SCREEN_X_BYTES + 1])
            {
                // 两数据字不同，写入
                g_sc_write_address(sc, (x + G_SCREEN_X_BYTES) / 2, y - G_SCREEN_HEIGHT / 2);
                g_sc_write_byte_data(sc, data[x + y * G_SCREEN_X_BYTES]);
                g_sc_write_byte_data(sc, data[x + y * G_SCREEN_X_BYTES + 1]);
            }
        }
    }

    g_fb_destroy(sc->current);
    sc->current = g_fb_copy(sc->fb);
}

void g_sc_refresh_force(struct g_sc *sc)
{
    uint8_t *data = sc->fb->data;

    // 上半屏幕
    for (int y = 0; y < G_SCREEN_HEIGHT / 2; y++)
    {
        for (int x = 0; x < G_SCREEN_X_BYTES; x += 2)
        {
            g_sc_write_address(sc, x / 2, y);
            g_sc_write_byte_data(sc, data[x + y * G_SCREEN_X_BYTES]);
            g_sc_write_byte_data(sc, data[x + y * G_SCREEN_X_BYTES + 1]);
        }
    }

    // 下半屏幕
    for (int y = G_SCREEN_HEIGHT / 2; y < G_SCREEN_HEIGHT; y++)
    {
        for (int x = 0; x < G_SCREEN_X_BYTES; x += 2)
        {
            g_sc_write_address(sc, (x + G_SCREEN_X_BYTES) / 2, y - G_SCREEN_HEIGHT / 2);
            g_sc_write_byte_data(sc, data[x + y * G_SCREEN_X_BYTES]);
            g_sc_write_byte_data(sc, data[x + y * G_SCREEN_X_BYTES + 1]);
        }
    }

    g_fb_destroy(sc->current);
    sc->current = g_fb_copy(sc->fb);
}
