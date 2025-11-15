from px import clcd,keyboard
import machine
import time
import network
import urequests
import ntptime

WIFI_SSID="WIFI_NAME"
WIFI_PASS="WIFI_PASSWORD"
NTP_HOST="ntp.jst.mfeed.ad.jp"
BITFLYERAPI_BASE="https://api.bitflyer.com/v1/"
TICKER_INTERVAL_MS = 10 * 1000

clcd.clear()
clcd.set_cursor(0, 0)
print("Connect " + WIFI_SSID[0:12])

wlan = network.WLAN()
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)

while not wlan.isconnected():
    machine.idle()

clcd.set_cursor(1, 0)
print("OK. " + wlan.ipconfig("addr4")[0])

rtc = machine.RTC()
ntptime.host = NTP_HOST
ntptime.settime()
ticker_update_timer = 0

key = None
while key is None:
    if time.ticks_diff(time.ticks_ms(), ticker_update_timer) >= TICKER_INTERVAL_MS:
        ticker_update_timer = time.ticks_ms()
        now = time.localtime(time.time() + 9 * 3600)
        clcd.set_cursor(2, 0)
        print(f'{now[0]}/{now[1]}/{now[2]} {now[3]:02}:{now[4]:02}:{now[5]:02}')

        ticker_ep = BITFLYERAPI_BASE + "ticker?product_code=BTC_JPY"
        clcd.set_cursor(3, 0)
        print("BTC/JPY ")
        resp = urequests.get(ticker_ep)
        ticker = resp.json()
        print(ticker["ltp"])

    machine.idle()

    keyboard.update()
    key = keyboard.get_new_key()
