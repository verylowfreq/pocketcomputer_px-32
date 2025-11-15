from px import *
import time
from machine import Pin, I2C
import struct

class EnvUnitIV:
    ADDR_SHT40 = 0x44
    ADDR_BMP280 = 0x76

    def __init__(self, bus:I2C) -> None:
        self.bus = bus
        self.val_tempearture = -1
        self.val_pressure = -1
        self.val_humidity = -1

    def update(self) -> None:
        self.bus.writeto(self.ADDR_SHT40, b'\xf6')
        time.sleep_ms(10)
        resp = self.bus.readfrom(self.ADDR_SHT40, 6)
        tb_1 = resp[0]
        tb_2 = resp[1]
        tb_word = tb_1 * 256 + tb_2
        self.val_temperature = -45 + 175 * (tb_word / 65535)
        hb_1 = resp[3]
        hb_2 = resp[4]
        hb_word = hb_1 * 256 + hb_2
        self.val_humidity = -6 + 125 * (hb_word / 65535)
        
        self.update_bmp280_pressure()

    def update_bmp280_pressure(self) -> None:
        #self.bus.writeto(self.ADDR_BMP280, b'\xf4\x25')
        self.bus.writeto_mem(self.ADDR_BMP280, 0xF4, b'\x27')
        self.bus.writeto_mem(self.ADDR_BMP280, 0xF5, b'\xA0')

        data = self.bus.readfrom_mem(self.ADDR_BMP280, 0xF7, 6)
        adc_P = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_T = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

        self.dig_T1, self.dig_T2, self.dig_T3, \
        self.dig_P1, self.dig_P2, self.dig_P3, \
        self.dig_P4, self.dig_P5, self.dig_P6, \
        self.dig_P7, self.dig_P8, self.dig_P9 = \
            struct.unpack("<HhhHhhhhhhhh", self.bus.readfrom_mem(self.ADDR_BMP280, 0x88, 24))

        var1 = (adc_T / 16384.0 - self.dig_T1 / 1024.0) * self.dig_T2
        var2 = ((adc_T / 131072.0 - self.dig_T1 / 8192.0) ** 2) * self.dig_T3
        self.t_fine = var1 + var2
        T = self.t_fine / 5120.0

        var1 = self.t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * self.dig_P6 / 32768.0
        var2 = var2 + var1 * self.dig_P5 * 2.0
        var2 = var2 / 4.0 + self.dig_P4 * 65536.0
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1
        if var1 == 0:
            return
        p = 1048576.0 - adc_P
        p = ((p - var2 / 4096.0) * 6250.0) / var1
        var1 = self.dig_P9 * p * p / 2147483648.0
        var2 = p * self.dig_P8 / 32768.0
        p = p + (var1 + var2 + self.dig_P7) / 16.0
        self.val_pressure = p / 100
        

    def __read_bmp280_2bytes(self, upper_addr) -> bytes:
        self.bus.writeto(self.ADDR_BMP280, upper_addr)
        b1 = self.bus.readfrom(self.ADDR_BMP280, 1)
        self.bus.writeto(self.ADDR_BMP280, upper_addr + 1)
        b2 = self.bus.readfrom(self.ADDR_BMP280, 1)
        return bytes([b1, b2])
    
    def __read_bmp280_u16(self, upper_addr) -> int:
        ba = self.__read_bmp280_2bytes(upper_addr)
        val = struct.unpack('>H', ba)[0]
        
    def __read_bmp280_s16(self, upper_addr) -> int:
        ba = self.__read_bmp280_2bytes(upper_addr)
        val = struct.unpack('>h', ba)[0]

    def bmp280_compensation(self, t_fine) -> None:
        pass


    def get_temperature(self) -> float:
        return self.val_temperature
    
    def get_pressure(self) -> float:
        return self.val_pressure
    
    def get_humidity(self) -> float:
        return self.val_humidity

pin_scl = Pin(39)
pin_sda = Pin(40)

wire = I2C(scl=pin_scl, sda=pin_sda, freq=100000)

envunit = EnvUnitIV(wire)
clcd.clear()
count = 0
timer = time.ticks_ms()
key = None
while key is None:
    now = time.ticks_ms()
    if time.ticks_diff(now, timer) >= 1000:
        timer = now
        envunit.update()
        clcd.set_cursor(0, 0)
        clcd.print(f'uptime={count}')
        clcd.set_cursor(1, 0)
        val_temperature = envunit.get_temperature()
        clcd.print(f't[c]={val_temperature:4.1f}')
        clcd.set_cursor(2, 0)
        clcd.print(f'rh[%]={envunit.get_humidity():5.1f}')
        clcd.set_cursor(3, 0)
        clcd.print(f'p[hPa]={envunit.get_pressure():8.2f}')
        count += 1
    keyboard.update()
    key = keyboard.get_new_key()
