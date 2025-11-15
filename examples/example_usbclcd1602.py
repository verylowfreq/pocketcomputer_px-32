import time, machine, io

PIN_SCL = machine.Pin(2)
PIN_SDA = machine.Pin(1)
wire = machine.I2C(freq=400000,scl=PIN_SCL,sda=PIN_SDA)

class CLCD(io.IOBase):
    CLCD_ADDR = 0x2f

    def __init__(self, wire):
        self.wire = wire

    def clear(self):
        self.wire.writeto(self.CLCD_ADDR, b'\x02\x01')
        time.sleep_ms(5)
        
    def set_cursor(self, row, col):
        row = row % 2
        col = col % 2
        self.wire.writeto(self.CLCD_ADDR, bytes([0x02, 0x80 + 0x40 * row + col]))

    def print(self, text):
        for ch in text:
            self.wire.writeto(self.CLCD_ADDR, bytes([ 0x01, ord(ch) ]))
            
    def write(self, b):
        if b == b'\n':
            self.set_curosr(0, 0)
        else:
            for ch in b:
                self.wire.writeto(self.CLCD_ADDR, bytes([ 0x01, ch ]))

    def readinto(self):
        return None


clcd = CLCD(wire)
clcd.clear()
clcd.print("Hello, uPython!")
time.sleep_ms(2000)
clcd.clear()
clcd.set_cursor(1, 0)
clcd.print("Have a nice day!")

# import os
# os.dupterm(clcd)
