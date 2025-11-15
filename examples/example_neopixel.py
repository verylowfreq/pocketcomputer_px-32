import machine, neopixel, time

PIN_NEOPIXEL = machine.Pin(21)
led = neopixel.NeoPixel(PIN_NEOPIXEL, 1)

led[0] = (255, 0, 0)
led.write()
time.sleep_ms(500)

led[0] = (0, 255, 0)
led.write()
time.sleep_ms(500)

led[0] = (0, 0, 255)
led.write()
time.sleep_ms(500)

while True:
    led[0] = (128, 128, 128)
    led.write()
    time.sleep_ms(250)

    led[0] = (0, 0, 0)
    led.write()
    time.sleep_ms(750)    
