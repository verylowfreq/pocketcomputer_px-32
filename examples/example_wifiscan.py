from px import *
from network import WLAN
nic=WLAN(WLAN.IF_STA)
nic.active(True)
aps=nic.scan()
for ap in aps:
  clcd.clear()
  clcd.set_cursor(0,0)
  clcd.print(ap)
  keyboard.wait_any_key()
