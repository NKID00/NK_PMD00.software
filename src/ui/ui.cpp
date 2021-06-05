/**
 * 使用 MIT License 进行许可。
 * SPDX-License-Identifier: MIT
 * 版权所有 © 2020-2021 NKID00
 */

#include <unistd.h>

#include <gpiod.h>
#include "sqlite3.h"

#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <ctime>
#include <cwchar>
#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>

#include "g12864/g12864.h"

#ifndef NK_PMD00_VERSION
#define NK_PMD00_VERSION "未知"
#endif
#ifndef NK_PMD00_COMMIT
#define NK_PMD00_COMMIT "未知"
#endif
#ifndef NK_PMD00_BUILD
#define NK_PMD00_BUILD "未知"
#endif

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

#ifndef DEBUG
#define g_info(s) std::cout << s << "... " << std::flush
#else
#define g_info(s) std::cout << "[" << __func__ << ":" << __LINE__ << "] " << s << "... " << std::flush
#endif
#define g_info_done() std::cout << "完成" << std::endl

#define dt_ms(t0, t1) (((t1).tv_sec - (t0).tv_sec) * 1000 + ((t1).tv_nsec - (t0).tv_nsec) / 1000000.0)

std::uint8_t *font;

class UI
{
public:
    UI(struct g_fb *fb) : fb(fb), selected(0), highlight_selected(false) {}

    void process(Event event)
    {
        switch (event)
        {
        case Event::Up:
            if (selected > 0)
            {
                selected--;
                refresh();
            }
            break;
        case Event::Down:
            if (selected < 3)
            {
                selected++;
                refresh();
            }
            break;
        }
    }

    void refresh()
    {
        g_fb_fill(fb, false);
        for (int i = 0; i < 4; i++)
        {
            if (highlight_selected && i == selected)
            {
                g_fb_draw_rect(fb, 0, i * 16, 127, i * 16 + 15, true);
                g_fb_draw_text(fb, 0, i * 16, items[i].c_str(), false, font);
            }
            else
            {
                g_fb_draw_text(fb, 0, i * 16, items[i].c_str(), true, font);
            }
        }
    }

protected:
    struct g_fb *fb;
    std::wstring items[4];
    int selected;
    bool highlight_selected;
};

class TitleUI : public UI
{
public:
    TitleUI(struct g_fb *fb) : UI(fb), selected(0), highlight_selected(false) {}

    void process(Event event)
    {
        switch (event)
        {
        case Event::Up:
            if (selected > 0)
            {
                selected--;
                refresh();
            }
            break;
        case Event::Down:
            if (selected < items.size())
            {
                selected++;
                refresh();
            }
            break;
        }
    }

    void refresh()
    {
        UI::items[0] = title;
        if (items.size() == 0)
        {
            UI::items[1] = L"(none)";
            UI::items[2] = L"";
            UI::items[3] = L"";
            UI::highlight_selected = false;
        }
        else if (items.size() <= 3)
        {
            for (size_t i = 0; i < 3; i++)
            {
                if (items.size() > i)
                {
                    UI::items[i + 1] = items[i];
                }
                else
                {
                    UI::items[i + 1] = L"";
                }
            }
            UI::selected = selected + 1;
            UI::highlight_selected = highlight_selected;
        }
        else
        {
            if (selected == 0)
            {
                for (size_t i = 0; i < 3; i++)
                {
                    UI::items[i + 1] = items[i];
                }
                UI::selected = 1;
            }
            else if (selected == items.size() - 1)
            {
                for (size_t i = 0; i < 3; i++)
                {
                    UI::items[3 - i] = items[selected - i];
                }
                UI::selected = 3;
            }
            else
            {
                UI::items[1] = items[selected - 1];
                UI::items[2] = items[selected];
                UI::items[3] = items[selected + 1];
                UI::selected = 2;
            }
            UI::highlight_selected = highlight_selected;
        }
        UI::refresh();
    }

protected:
    std::wstring title;
    std::vector<std::wstring> items;
    size_t selected;
    bool highlight_selected;
};

static int sqlite3_words_callback(void *data, int argc, char **argv, char **col_name);

std::wstring utf8_to_wchar(std::string s)
{
    auto state = std::mbstate_t();
    auto c_s = s.c_str();
    auto len = 1 + std::mbsrtowcs(nullptr, &c_s, 0, &state);
    wchar_t wstr[len];
    std::mbsrtowcs(wstr, &c_s, len, &state);
    return std::wstring(wstr);
}

std::string wchar_to_utf8(std::wstring ws)
{
    auto state = std::mbstate_t();
    auto c_ws = ws.c_str();
    auto len = 1 + std::wcsrtombs(nullptr, &c_ws, 0, &state);
    char str[len];
    std::wcsrtombs(str, &c_ws, len, &state);
    return std::string(str);
}

class DictionaryUI : public TitleUI
{
public:
    DictionaryUI(struct g_fb *fb, const char *db_file) : TitleUI(fb), word(L""), display_info(false), pervious_event(Event::None)
    {
        sqlite3_open(db_file, &db);
    }

    /*
    abc  def  gh   Up(1)
    ijk  lmn  opq  Down(2)
    rst  uvw  xyz  Left(3)
              Back Right
    */
    void process(Event event)
    {
        if (display_info)
        {
            switch (event)
            {
            case Event::Up:
                if (TitleUI::selected > 0)
                {
                    TitleUI::selected--;
                    refresh();
                }
                break;
            case Event::Down:
                if (TitleUI::selected < items.size())
                {
                    TitleUI::selected++;
                    refresh();
                }
                break;
            case Event::Left:
            case Event::Back:
                display_info = false;
                TitleUI::selected = pervious_selected;
                update_items_words();
                refresh();
                break;
            }
        }
        else
        {
            switch (event)
            {
            case Event::Key1:
            case Event::Key2:
            case Event::Key3:
            case Event::Key4:
            case Event::Key5:
            case Event::Key6:
            case Event::Key7:
            case Event::Key8:
            case Event::Key9:
                pervious_event = event;
                break;
            case Event::Up:
                if (pervious_event == Event::None)
                {
                    if (TitleUI::selected > 0)
                    {
                        TitleUI::selected--;
                        refresh();
                    }
                }
                else
                {
                    switch (pervious_event)
                    {
                    case Event::Key1:
                        word_append(L'a');
                        break;
                    case Event::Key2:
                        word_append(L'd');
                        break;
                    case Event::Key3:
                        word_append(L'g');
                        break;
                    case Event::Key4:
                        word_append(L'i');
                        break;
                    case Event::Key5:
                        word_append(L'l');
                        break;
                    case Event::Key6:
                        word_append(L'o');
                        break;
                    case Event::Key7:
                        word_append(L'r');
                        break;
                    case Event::Key8:
                        word_append(L'u');
                        break;
                    case Event::Key9:
                        word_append(L'x');
                        break;
                    }
                    pervious_event = Event::None;
                }
                break;
            case Event::Down:
                if (pervious_event == Event::None)
                {
                    if (TitleUI::selected < items.size())
                    {
                        TitleUI::selected++;
                        refresh();
                    }
                }
                else
                {
                    switch (pervious_event)
                    {
                    case Event::Key1:
                        word_append(L'b');
                        break;
                    case Event::Key2:
                        word_append(L'e');
                        break;
                    case Event::Key3:
                        word_append(L'h');
                        break;
                    case Event::Key4:
                        word_append(L'j');
                        break;
                    case Event::Key5:
                        word_append(L'm');
                        break;
                    case Event::Key6:
                        word_append(L'p');
                        break;
                    case Event::Key7:
                        word_append(L's');
                        break;
                    case Event::Key8:
                        word_append(L'v');
                        break;
                    case Event::Key9:
                        word_append(L'y');
                        break;
                    }
                    pervious_event = Event::None;
                }
                break;
            case Event::Left:
                if (pervious_event == Event::None)
                {
                    if (!word.empty())
                    {
                        word.pop_back();
                        update_items_words();
                        refresh();
                    }
                }
                else
                {
                    switch (pervious_event)
                    {
                    case Event::Key1:
                        word_append(L'c');
                        break;
                    case Event::Key2:
                        word_append(L'f');
                        break;
                    case Event::Key4:
                        word_append(L'k');
                        break;
                    case Event::Key5:
                        word_append(L'n');
                        break;
                    case Event::Key6:
                        word_append(L'q');
                        break;
                    case Event::Key7:
                        word_append(L't');
                        break;
                    case Event::Key8:
                        word_append(L'w');
                        break;
                    case Event::Key9:
                        word_append(L'z');
                        break;
                    }
                    pervious_event = Event::None;
                }
                break;
            case Event::Right:
                pervious_event = Event::None;
                pervious_selected = selected;
                display_info = true;
                title = items[selected];
                update_items_info();
                refresh();
            case Event::Back:
                pervious_event = Event::None;
                if (!word.empty())
                {
                    word = L"";
                    update_items_words();
                    refresh();
                }
            }
        }
    }

    void refresh()
    {
        title = word + L"|";
        highlight_selected = !display_info;
        TitleUI::refresh();
    }

    void word_append(wchar_t s)
    {
        word.push_back(s);
        update_items_words();
        refresh();
    }

    void update_items_words()
    {
        char *zErrMsg = 0;
        std::stringstream ss;
        ss << "SELECT * FROM ecdict WHERE word LIKE \"" << wchar_to_utf8(word) << "%\" AND word NOT LIKE \"% %\" AND collins > 0 AND (translation LIKE \"%\" + CHAR(10) + \"%\" OR (translation NOT LIKE \"%abbr.%\" AND translation NOT LIKE \"%[网络]%\" AND translation NOT LIKE \"%[地名]%\" AND translation NOT LIKE \"%[医]%\" AND translation NOT LIKE \"%[药]%\" AND translation NOT LIKE \"%[化]%\")) AND word NOT LIKE \"%(%\" AND word NOT LIKE \"%（%\" LIMIT 20;";
        // ss << "SELECT * FROM ecdict WHERE word LIKE \"" << wchar_to_utf8(word) << "%\" LIMIT 20;";
        TitleUI::items.clear();
        if (sqlite3_exec(db, ss.str().c_str(), sqlite3_words_callback, this, &zErrMsg))
        {
            g_info("数据查询失败: ") << zErrMsg << std::endl;
            sqlite3_free(zErrMsg);
        }
        TitleUI::selected = 0;
    }

    void update_items_words_callback(int argc, char **argv, char **col_name)
    {
        std::string target = "word";
        for (int i = 0; i < argc; i++)
        {
            if (col_name[i] == target)
            {
                TitleUI::items.push_back(utf8_to_wchar(argv[i]));
            }
        }
    }

    void update_items_info()
    {
    }

    void t()
    {
        word = L"abandona";
        update_items_words();
        refresh();
    }

    void t2()
    {
        word = L"abandon";
        update_items_words();
        refresh();
    }

protected:
    std::wstring word;
    bool display_info;
    Event pervious_event;
    int pervious_selected;
    sqlite3 *db;
};

static int sqlite3_words_callback(void *data, int argc, char **argv, char **col_name)
{
    (reinterpret_cast<DictionaryUI *>(data))->update_items_words_callback(argc, argv, col_name);
    return 0;
}
