from micropython import const, schedule
import machine, time
from machine import Pin, I2C


class SubMCUCommunicator:
    """SubMCU has CLCD and Keyboard, and connected to main MCU via I2C"""

    TARGET_ADDR = const(0x2e)
    def __init__(self, wire:machine.I2C) -> None:
        self.wire = wire
        self.clcd = CLCD(self)
        self.keyboard = Keyboard(self)

    def begin(self) -> None:
        pass

    def write(self, data:bytes) -> None:
        while len(data) > 0:
            copylen = min(30, len(data))
            self.wire.writeto(self.TARGET_ADDR, data[0:copylen])
            data = data[copylen:]

    def read(self, command:bytes, nread:int) -> bytes:
        if len(command) > 0:
            self.wire.writeto(self.TARGET_ADDR, command)
        return self.wire.readfrom(self.TARGET_ADDR, nread)

    def get_clcd(self) -> CLCD:
        return self.clcd
    
    def get_keyboard(self) -> Keyboard:
        return self.keyboard


class CLCD:
    """Character LCD 20x4 with alphanumerical and katanaka fonts"""

    def __init__(self, submcu:SubMCUCommunicator) -> None:
        self.comm = submcu

    def begin(self) -> None:
        pass

    def clear(self) -> None:
        self.comm.write(bytes([0x02, 0x01]))
        time.sleep_ms(5)

    def set_cursor(self, row:int, col:int) -> None:
        row, col = row % 4, col % 20
        addr = col
        if row == 1: addr += 0x40
        elif row == 2: addr += 20
        elif row == 3: addr += 0x40 + 20
        self.comm.write(bytes([0x02, 0x80 + addr]))

    def show_cursor(self, underline:bool, block:bool) -> None:
        val = 0x0c + (0x02 if underline else 0x00) + (0x01 if block else 0x00)
        self.comm.write(bytes([0x02, val]))

    def print(self, *values) -> None:
        for i, val in enumerate(values):
            s = str(val)
            if len(values) > 0 and i != len(values) - 1:
                s += " "
            commands = bytearray()
            for ch in s:
                commands += [0x01] + [ord(ch)]
            self.comm.write(commands)


class Keyboard:
    """JP layout Keyboard"""

    KC_SYM = 0x01
    KC_CAPS = 0x02
    KC_PM = 0x03
    KC_LEFT = 0x04
    KC_UP = 0x05
    KC_DOWN = 0x06
    KC_RIGHT = 0x07

    KC_POWER = 0x81  # GPIO12
    KC_MENU = 0x82  # GPIO13
    KC_RUN = 0x83  # GPIO14
    KC_STOP = 0x84  # GPIO15


    #FIXME: ESP32S3に接続されているMENU,RUN,STOP,POWERボタンにも対応する

    # KC_A, KC_Z = 4, 29
    # KC_1, KC_0 = 0x1e, 0x27
    # KC_ENTER, KC_ESC, KC_BS = 40, 41, 42
    # KC_RIGHT, KC_LEFT, KC_DOWN, KC_UP = 0x4F, 0x50, 0x51, 0x52
    # KC_APP = 0x65
    # KC_SPACE = 44
    # KEYCODE_MAP = {
    #     0x2d: '-', 0x2e: '^', 0x2f: '@',
    #     0x30: '[', 0x32: ']', 0x33: ';', 0x34: ':',
    #     0x36: ',', 0x37: '.', 0x38: '/',
    #     0x87: '\\', 0x89: '|'
    # }
    # SHIFT_MAP = {
    #     'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G', 'h': 'H', 'i': 'I',
    #     'j': 'J', 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N', 'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R',
    #     's': 'S', 't': 'T', 'u': 'U', 'v': 'V', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z',
    #     '1': '!', '2': '"', '3': '#', '4': '$', '5': '%', '6': '&', '7': '\'', '8': '(',
    #     '9': ')', '0': '', '.': '>', ',': '<', '/': '?', '-': '=', '^': '~', '@': '`',
    #     '[': '{', ']': '}', ';': '+', ':': '*', '\\': '_', 
    # }

    def __init__(self, submcu:SubMCUCommunicator):
        self.comm = submcu
        self.prev_report = b'\x00' * 8
        self.report = b'\x00' * 8
#         self.btn_power = Pin(12, Pin.IN, Pin.PULL_UP)
#         self.btn_menu = Pin(13, Pin.IN, Pin.PULL_UP)
#         self.btn_run = Pin(14, Pin.IN, Pin.PULL_UP)
#         self.btn_stop = Pin(15, Pin.IN, Pin.PULL_UP)
        self.btn_power = BTN_POWER
        self.btn_menu = BTN_MENU
        self.btn_run = BTN_RUN
        self.btn_stop = BTN_STOP

    def update(self) :
        self.report = self.comm.read(bytes([0x05]), 8)
        if not self.btn_power.value():
            self.report = bytes([ self.KC_POWER ]) + self.report[0:5]
        if not self.btn_menu.value():
            self.report = bytes([ self.KC_MENU ]) + self.report[0:5]
        if not self.btn_run.value():
            self.report = bytes([ self.KC_RUN ]) + self.report[0:5]
        if not self.btn_stop.value():
            self.report = bytes([ self.KC_STOP ]) + self.report[0:5]

    def get_new_key(self):
        """
        新しく押されたキーを取得する。
        Returns: str | int | None
        """
        if self.report == self.prev_report:
            # 変化がない == 新たな入力キーがない
            return None
        # if self.report[2] == self.prev_report[2]:
        #     # 先頭キーが同じ == おそらく同時押しなので、非対応とする
        #     self.prev_report = self.report
        #     return None

        self.prev_report = self.report

        if sum(self.report) == 0:
            # すべて 0x00 == なにも押されていない
            return None

        # mod, keycode = self.report[0], self.report[2]
        # is_shift = (mod & 0x22) != 0

        keycode = self.report[0]

        # 特殊キーを文字または定数に変換
        # if keycode == self.KC_ENTER: return '\n'
        # if keycode == self.KC_BS: return '\b'
        # if keycode in [self.KC_UP, self.KC_DOWN, self.KC_LEFT, self.KC_RIGHT]:
        #     return keycode
        if (0x01 <= keycode and keycode <= 0x07) or (0x81 <= keycode and keycode <= 0x84):
            return keycode
        else:
            return chr(keycode)

        # 文字キー
        # char = None
        # if self.KC_A <= keycode <= self.KC_Z:
        #     char = chr(ord('a') + keycode - self.KC_A)
        # elif self.KC_1 <= keycode <= self.KC_0:
        #     if keycode == self.KC_0:
        #         char = '0'
        #     else:
        #         char = chr(ord('1') + keycode - self.KC_1)
        # elif keycode == self.KC_SPACE:
        #     char = ' '
        # elif keycode in self.KEYCODE_MAP:
        #     char = self.KEYCODE_MAP[keycode]

        # if char is not None:
        #     if is_shift:
        #         return self.SHIFT_MAP.get(char, char)
        #     else:
        #         return char
        # else:
        #     return None

    def wait_any_key(self):
        key = None
        while key is None:
            for _ in range(10):
                machine.idle()
            self.update()
            key = self.get_new_key()
        return key


def stop_handler(pin):
    if not BTN_POWER.value():
        machine.reset()


BTN_POWER = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
BTN_MENU = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
BTN_RUN = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
BTN_STOP = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

BTN_STOP.irq(stop_handler, machine.Pin.IRQ_FALLING)


PIN_SCL = machine.Pin(9)
PIN_SDA = machine.Pin(10)
wire2 = machine.I2C(1, scl=PIN_SCL, sda=PIN_SDA, freq=400000)

submcu = SubMCUCommunicator(wire2)
clcd = submcu.get_clcd()
keyboard = submcu.get_keyboard()

PIN_CLCD_BKL = Pin(11, Pin.OUT)
PIN_CLCD_BKL.value(True)
