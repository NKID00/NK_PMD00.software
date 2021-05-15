#ifndef __G_G12864_H__
#define __G_G12864_H__

#include <gpiod.h>
#include <stdbool.h>
#include <stdint.h>

#define G_SCREEN_WIDTH 128
#define G_SCREEN_HEIGHT 64

#define G_BL_ON 1
#define G_BL_OFF 0

#define g_info(s) printf("[%s:%ld] %s... ", __func__, __LINE__, s)
#define g_info_done() printf("完成\n")

/**
 * @brief 帧缓存（Frame Buffer）
 */
struct g_fb;

/**
 * @brief 屏幕（Screen）
 */
struct g_sc;

#ifdef __cplusplus
extern "C"
{
#endif

    /**
 * @brief 创建帧缓存
 */
    struct g_fb *
    g_fb_create();

    /**
 * @brief 销毁帧缓存
 */
    void g_fb_destroy(struct g_fb *fb);

    /**
 * @brief 获取帧缓存上坐标位置的字节
 */
    uint8_t *
    g_fb_get_byte(struct g_fb *fb, int x, int y);

    /**
 * @brief 获取帧缓存上坐标位置的像素
 */
    bool g_fb_get_pixel(struct g_fb *fb, int x, int y);

    /**
 * @brief 设置帧缓存上坐标位置的像素
 */
    void g_fb_set_pixel(struct g_fb *fb, int x, int y, bool value);

    /**
 * @brief 复制帧缓存
 */
    struct g_fb *
    g_fb_copy(struct g_fb *fb_src);

    /**
 * @brief 填充帧缓存
 */
    void g_fb_fill(struct g_fb *fb, bool value);

    /**
 * @brief 在帧缓存上绘制矩形
 */
    void g_fb_draw_rect(struct g_fb *fb, int x0, int y0, int x1, int y1, bool value);

    /**
 * @brief 在帧缓存上绘制 ASCII 字符
 */
    void g_fb_draw_char_ascii(struct g_fb *fb, int x, int y, wchar_t ch, bool value, uint8_t *font);

    /**
 * @brief 在帧缓存上绘制 Unicode 字符
 */
    void g_fb_draw_char_unicode(struct g_fb *fb, int x, int y, wchar_t ch, bool value, uint8_t *font);

    /**
 * @brief 在帧缓存上绘制字符
 */
    void g_fb_draw_char(struct g_fb *fb, int x, int y, wchar_t ch, bool value, uint8_t *font);

    /**
 * @brief 在帧缓存上绘制字符串
 */
    void g_fb_draw_text(struct g_fb *fb, int x, int y, wchar_t *text, bool value, uint8_t *font);

    /**
 * @brief 短暂延时
 */
    void g_delay();

    /**
 * @brief 创建屏幕
 */
    struct g_sc *
    g_sc_create(struct gpiod_line *sid,
                struct gpiod_line *sclk,
                struct gpiod_line *bla);

    /**
 * @brief 销毁屏幕
 */
    void g_sc_destroy(struct g_sc *sc);

    /**
 * @brief 获取屏幕帧缓存
 */
    struct g_fb *
    g_sc_get_fb(struct g_sc *sc);

    /**
 * @brief 设置屏幕背光
 */
    void g_sc_set_bl(struct g_sc *sc, int value);

    /**
 * @brief 写入高电平位
 */
    void g_sc_write_bit_high(struct g_sc *sc);

    /**
 * @brief 写入低电平位
 */
    void g_sc_write_bit_low(struct g_sc *sc);

    /**
 * @brief 写入位
 */
    void g_sc_write_bit(struct g_sc *sc, int value);

    /**
 * @brief 写入字节
 */
    void g_sc_write_byte(struct g_sc *sc, int rs, uint8_t value);

    /**
 * @brief 写入指令字节
 */
    void g_sc_write_byte_command(struct g_sc *sc, uint8_t value);

    /**
 * @brief 写入数据字节
 */
    void g_sc_write_byte_data(struct g_sc *sc, uint8_t value);

    /**
 * @brief 写入初始设置
 */
    void g_sc_write_setup(struct g_sc *sc);

    /**
 * @brief 写入绘图 RAM 地址（x 单位为 16 位字）
 */
    void g_sc_write_address(struct g_sc *sc, int x, int y);

    /**
 * @brief 刷新画面（仅刷新改变的数据字）
 */
    void g_sc_refresh(struct g_sc *sc);

    /**
 * @brief 强制刷新画面（刷新所有数据字）
 */
    void g_sc_refresh_force(struct g_sc *sc);

#ifdef __cplusplus
}
#endif

#endif /* __G_G12864_H__ */