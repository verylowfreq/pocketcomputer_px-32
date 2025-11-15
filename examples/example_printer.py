from px import clcd,keyboard
import time
import machine
from machine import Pin,UART
import sys
import gc

ser_tx = Pin(41)
ser_rx = Pin(42)
ser = UART(1, 9600, tx=ser_tx, rx=ser_rx)

ser.write(b'---- ----')
ser.write(b"Self test\n\n")

ser.write("PocketComputer PX-32\n")
ser.write("    by Mitsumine Suzu\n")
ser.write("MicroPython ")
ser.write(".".join([str(v) for v in sys.implementation.version[0:3]]))
ser.write("\n")
ser.write('CPU Freq: ' + str(machine.freq()) + '\n')
ser.write("Mem Alloc: " + str(gc.mem_alloc()))

ser.write("\n\n\n")
