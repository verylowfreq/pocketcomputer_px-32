# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import builtins
from px import clcd, keyboard
import time
import machine
import micropython

orig_print = builtins.print

def clcd_print(*args) -> None:
    clcd.print(*args)
    orig_print(*args)

def clcd_input(prompt="") -> str:
    buf = ""
    clcd.set_cursor(3, 0)
    clcd.print(" " * 20)
    clcd.set_cursor(3, 0)
    clcd.print(prompt)
    clcd.show_cursor(1, 0)
    cur = 0
    while True:
        key = None
        while key is None:
            keyboard.update()
            key = keyboard.get_new_key()
            time.sleep_ms(10)

        if key is not None:
            if isinstance(key, str):
                if key == '\n':
                    # 入力を確定
                    return buf
                elif key == '\b':
                    if len(buf) > 0:
                        prev = buf[0:cur-1]
                        forward = buf[cur:]
                        buf = prev + forward
                        cur -= 1
                else:
                    prev = buf[0:cur]
                    forward = buf[cur:]
                    buf = prev + key + forward
                    cur += 1
            elif key == px.keyboard.KC_RIGHT:
                cur = min(len(buf), cur + 1)
            elif key == px.keyboard.KC_LEFT:
                cur = max(0, cur - 1)


        line_to_print = prompt + buf
        if len(line_to_print) > 18:
            line_to_print = line_to_print[len(line_to_print - 20)]
        else:
            while len(line_to_print) < 20:
                line_to_print += " "
        clcd.set_cursor(3, 0)
        clcd.print(line_to_print)
        clcd.set_cursor(3, len(prompt) + cur)


builtins.print = clcd_print
builtins.input = clcd_input
