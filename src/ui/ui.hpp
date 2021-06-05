#include <cstdint>

#ifndef DEBUG
#define g_info(s) std::cout << s << "... " << std::flush
#else
#define g_info(s) std::cout << "[" << __func__ << ":" << __LINE__ << "] " << s << "... " << std::flush
#endif
#define g_info_done() std::cout << "完成" << std::endl

#define dt_ms(t0, t1) (((t1).tv_sec - (t0).tv_sec) * 1000 + ((t1).tv_nsec - (t0).tv_nsec) / 1000000.0)

extern std::uint8_t *font;
