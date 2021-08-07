#include <unistd.h>

#include <gpiod.h>

#include "g12864/g12864.h"

#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <ctime>
#include <cwchar>
#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>

#ifndef DEBUG
#define g_info(s) std::cout << s << "... " << std::flush
#else
#define g_info(s) std::cout << "[" << __func__ << ":" << __LINE__ << "] " << s << "... " << std::flush
#endif
#define g_info_done() std::cout << "完成" << std::endl

#define dt_ms(t0, t1) (((t1).tv_sec - (t0).tv_sec) * 1000 + ((t1).tv_nsec - (t0).tv_nsec) / 1000000.0)

constexpr int SCREEN_SID = 23;  // 物理编号 16
constexpr int SCREEN_SCLK = 24; // 物理编号 18
constexpr int SCREEN_BLA = 12;  // 物理编号 32

constexpr int K_ROW0 = 4;  // 物理编号 7
constexpr int K_ROW1 = 17; // 物理编号 11
constexpr int K_ROW2 = 27; // 物理编号 13
constexpr int K_ROW3 = 22; // 物理编号 15
constexpr int K_COL0 = 5;  // 物理编号 29
constexpr int K_COL1 = 6;  // 物理编号 31
constexpr int K_COL2 = 13; // 物理编号 33
constexpr int K_COL3 = 26; // 物理编号 37

constexpr const char *K_CONSUMER = "keyboard";

constexpr int K_LOW = 0;
constexpr int K_HIGH = 1;

enum class Event
{
    Key1,
    Key2,
    Key3,
    Key4,
    Key5,
    Key6,
    Key7,
    Key8,
    Key9,
    Up,
    Down,
    Left,
    Right,
    Back,
    None
};

extern std::uint8_t *font;
