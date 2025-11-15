from px import *
import time
from machine import Pin,PWM
DUTY_MIN=40
DUTY_MAX=115
DUTY_CENTER=77
p=Pin(1)
s=PWM(p,freq=50,duty=DUTY_CENTER)
key=None
while key is None:
  keyboard.update()
  key=keyboard.get_new_key()
  for d in range(DUTY_MIN,DUTY_MAX):
    s.duty(d)
    time.sleep_ms(20)
  for d in range(DUTY_MIN,DUTY_MAX):
    s.duty(DUTY_MAX-d+DUTY_MIN)
    time.sleep_ms(10)
