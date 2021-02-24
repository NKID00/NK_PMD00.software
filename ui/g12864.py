# 使用 MIT License 进行许可。
# SPDX-License-Identifier: MIT
# 版权所有 © 2020-2021 NKID00

__all__ = ('SCREEN_WIDTH', 'SCREEN_HEIGHT', 'SCREEN_PIXELS', 'SCREEN_X_BYTES',
           'SCREEN_BYTES', 'Frame', 'Screen')

from time import time_ns
from itertools import islice

# 导入 ../util/util.py 里的函数
from importlib.util import spec_from_file_location, module_from_spec
_util_spec = spec_from_file_location('util', '../util/util.py')
_util = module_from_spec(_util_spec)
_util_spec.loader.exec_module(_util)
# 用 globals() 批量赋值的话错误检查程序就不高兴了
group_iter = _util.group_iter

# 一个字均指两个字节，而不是一个字符

# 常量
# SCREEN_WIDTH 必须是 16（一个字）的整数倍
SCREEN_WIDTH, SCREEN_HEIGHT = 128, 64
SCREEN_PIXELS = SCREEN_WIDTH * SCREEN_HEIGHT
SCREEN_X_BYTES = SCREEN_WIDTH // 8
SCREEN_BYTES = SCREEN_X_BYTES * SCREEN_HEIGHT
SCREEN_X_WORDS = SCREEN_X_BYTES // 2

T_MILLISECOND = 1 / 1000  # 毫秒
# T_MICROSECOND = T_MILLISECOND / 1000  # 微秒
# T_SCLK_HIGH = T_MICROSECOND * 5  # SCLK 每次保持高电平时间
# T_LCD_PROCESS = T_MICROSECOND * 72  # 液晶显示器执行指令时间
# 使用 timeit 在 Raspberry Pi zero + Raspberry Pi OS 下测试多次得：
#     pass 约延迟 0.19 微秒
#     sleep(0) 约延迟 7.9 微秒
#     sleep(T_MILLISECOND) 约延迟 1.15 毫秒
#     sleep(T_MICROSECOND) 约延迟 120 微秒
#     <OutputDevice>.on(); <...>.off() 约延迟 135 微秒
#     <OutputDevice>.value = 1; <...>.value = 0 约延迟 250 微秒
#     <PWMOutputDevice>.on(); <...>.off() 约延迟 240 微秒
#     <DigitalOutputDevice>.on(); <...>.off() 约延迟 385 微秒
# SCLK 每次保持高电平时间需要为约 5 微秒
# 液晶显示器执行其他指令时间为 72 微秒
#
# 因此尽可能使用 OutputDevice 的 .on() 和 .off() 进行操作

HIGH = True
LOW = False


class Frame:
    '''帧画面缓存'''

    def __init__(self, source=None):
        if isinstance(source, Frame):
            self._data = source._data.copy()
        elif isinstance(source, bytearray):
            self._data = source.copy()
        elif isinstance(source, bytes):
            self._data = bytearray(source)
        else:
            self._data = bytearray(SCREEN_BYTES)

    @staticmethod
    def point2index(x: int, y: int) -> int:
        '''将坐标转换为字节索引'''
        return x // 8 + y * SCREEN_X_BYTES

    def get_byte(self, x: int, y: int) -> int:
        '''获取索引位置的字节'''
        return self._data[self.point2index(x, y)]

    def set_byte(self, x: int, y: int, value: int):
        '''设置索引位置的字节'''
        self._data[self.point2index(x, y)] = value

    def get_pixel(self, x: int, y: int) -> bool:
        '''获取坐标位置的像素'''
        return self.get_byte(x, y) & (1 << (x % 8)) != 0

    def set_pixel(self, x: int, y: int, value: bool):
        '''设置坐标位置的像素'''
        if value:
            self.set_byte(
                x, y,
                self.get_byte(x, y) | (0b1000_0000 >> (x % 8))
            )
        else:
            self.set_byte(
                x, y,
                self.get_byte(x, y) & ~(0b1000_0000 >> (x % 8))
            )

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return self.get_pixel(key[0], key[1])
        elif isinstance(key, int):
            return self._data[key]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            return self.set_pixel(key[0], key[1], value)
        elif isinstance(key, int):
            self._data[key] = value

    def __iter__(self):
        yield from self._data

    def copy(self):
        '''复制自身'''
        return Frame(self)

    def fill(self, value: bool = False):
        '''填充'''
        if value:
            self._data = bytearray(b'\xff' * SCREEN_BYTES)
        else:
            self._data = bytearray(SCREEN_BYTES)

    def draw_rectangle(
        self,
        x0: int, y0: int,
        x1: int, y1: int,
        value: bool = True
    ):
        '''绘制矩形'''
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                self.set_pixel(x, y, value)

    def draw_line(
        self,
        x0: int, y0: int,
        x1: int, y1: int,
        value: bool = True
    ):
        '''绘制直线段'''
        pass


class Screen:
    '''双缓冲区屏幕'''

    def __init__(self, pin_sid, pin_sclk, pin_bla):
        '''创建屏幕实例，引脚编号为物理编号'''
        import RPi.GPIO
        self._gpio = RPi.GPIO
        self._gpio.setmode(self._gpio.BOARD)
        self._gpio.setup((pin_sid, pin_sclk, pin_bla), self._gpio.OUT)
        self._sid = pin_sid
        self._sclk = pin_sclk
        self._bla = self._gpio.PWM(pin_bla, 300)
        self._bla.start(0)
        self._bl_value = 0
        self.frame = Frame()
        self._current_frame = Frame()
        self.write_setup()

    def __del__(self):
        try:
            self._gpio.cleanup()
        except AttributeError:
            pass

    @property
    def bl_value(self):
        '''背光亮度，区间为 [0, 100]'''
        return self._bl_value

    @bl_value.setter
    def bl_value(self, value):
        self._bla.ChangeDutyCycle(value)
        self._bl_value = value

    def _write_bit(self, value: bool):
        '''写入位'''
        if value:
            self._write_bit_high()
        else:
            self._write_bit_low()

    def _write_bit_high(self):
        '''写入高电平位'''
        self._gpio.output(self._sid, HIGH)
        self._gpio.output(self._sclk, HIGH)
        self._gpio.output(self._sclk, LOW)

    def _write_bit_low(self):
        '''写入低电平位'''
        self._gpio.output(self._sid, LOW)
        self._gpio.output(self._sclk, HIGH)
        self._gpio.output(self._sclk, LOW)

    def write_byte(self, rs: bool, value):
        '''写入字节'''
        if isinstance(value, int):
            # 转换 int 到包含 bool 的 tuple，小索引对应低位
            value = tuple(map(
                lambda c: c == '1',
                '{:08b}'.format(value)[::-1]
            ))

        # 同步
        self._write_bit_high()
        self._write_bit_high()
        self._write_bit_high()
        self._write_bit_high()
        self._write_bit_high()

        # R/W
        self._write_bit_low()

        # RS
        self._write_bit(rs)

        # 间隔
        self._write_bit_low()

        # 高四位
        for bit in value[7:3:-1]:
            self._write_bit(bit)

        # 间隔
        self._write_bit_low()
        self._write_bit_low()
        self._write_bit_low()
        self._write_bit_low()

        # 低四位
        for bit in value[3::-1]:
            self._write_bit(bit)

        # 间隔
        self._write_bit_low()
        self._write_bit_low()
        self._write_bit_low()
        self._write_bit_low()

    def write_byte_command(self, value):
        '''写入指令字节，RS 为低电平'''
        self.write_byte(LOW, value)

    def write_byte_data(self, value):
        '''写入数据字节，RS 为高电平'''
        self.write_byte(HIGH, value)

    def write_word_data(self, byte0, byte1):
        '''写入数据字，RS 为高电平'''
        self.write_byte_data(byte0)
        self.write_byte_data(byte1)

    def write_setup(self):
        '''写入初始设置'''
        # 设置 8 位 MPU 接口，基本指令集
        self.write_byte_command(0b0011_0000)

        # 设置扩充指令集
        self.write_byte_command(0b0011_0100)

        # 设置绘图显示开
        self.write_byte_command(0b0011_0110)

    def write_address(self, x: int, y: int):
        '''写入绘图 RAM 地址，x 单位为字'''
        # 写入 y
        self.write_byte_command(0b1000_0000 + y)

        # 写入 x
        self.write_byte_command(0b1000_0000 + x)

    def refresh(self):
        '''刷新画面（仅刷新改变的字）'''
        # 计算当前帧变为下一帧需要改变的字
        for i, (current, target) in enumerate(zip(  # 每次迭代两帧相同位置的字
            group_iter(self._current_frame, 2),
            group_iter(self.frame, 2)
        )):
            if current != target:  # 两帧不同，写入数据
                if i < SCREEN_X_WORDS * SCREEN_HEIGHT // 2:
                    # 上半屏幕
                    self.write_address(
                        i % SCREEN_X_WORDS,
                        i // SCREEN_X_WORDS
                    )
                else:
                    # 下半屏幕
                    self.write_address(
                        i % SCREEN_X_WORDS + SCREEN_X_WORDS,
                        i // SCREEN_X_WORDS - SCREEN_HEIGHT // 2
                    )
                self.write_word_data(*target)

        self._current_frame = self.frame.copy()

    def refresh_force(self):
        '''强制刷新画面（刷新所有字）'''
        # 刷新所有字
        for i, target in enumerate(group_iter(self._current_frame, 2)):
            if i < SCREEN_X_WORDS * SCREEN_HEIGHT // 2:
                # 上半屏幕
                self.write_address(
                    i % SCREEN_X_WORDS,
                    i // SCREEN_X_WORDS
                )
            else:
                # 下半屏幕
                self.write_address(
                    i % SCREEN_X_WORDS + SCREEN_X_WORDS,
                    i // SCREEN_X_WORDS - SCREEN_HEIGHT // 2
                )
            self.write_word_data(*target)

        self._current_frame = self.frame.copy()


def test():
    print('创建屏幕实例并初始化... ', end='', flush=True)
    time_start = time_ns()
    s = Screen(
        pin_sid=16,
        pin_sclk=18,
        pin_bla=32
    )
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('调整背光亮度... ', end='', flush=True)
    time_start = time_ns()
    s.bl_value = 100
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('清屏... ', end='', flush=True)
    time_start = time_ns()
    s.refresh_force()
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('向帧缓存中绘制图案... ', end='', flush=True)
    time_start = time_ns()
    s.frame.fill(True)
    s.frame.draw_rectangle(10, 10, 100, 50, False)
    s.frame.draw_rectangle(30, 30, 41, 41, True)
    s.frame.draw_rectangle(30, 30, 40, 40, False)
    s.frame.draw_rectangle(29, 29, 39, 39, True)
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    print('刷新屏幕缓冲区... ', end='', flush=True)
    time_start = time_ns()
    s.refresh()
    print('用时 %.3f 毫秒' % ((time_ns() - time_start) / 1000000))

    input('完成。')


if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        print('已取消。', flush=True)
