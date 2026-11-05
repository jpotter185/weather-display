import time
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal
import os
import adafruit_connection_manager
import wifi
import adafruit_requests
from icons import get_icon
import adafruit_ntp
import rtc

SSID = os.getenv("CIRCUITPY_WIFI_SSID")
PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")
URL = os.getenv("WEATHER_API_URL")
WEATHER_PARAMS = (
    f"lat={os.getenv('LATITUDE')}"
    f"&lon={os.getenv('LONGITUDE')}"
)
BOARD_WIDTH = 64
BOARD_HEIGHT = 32
matrixportal = MatrixPortal(width=BOARD_WIDTH, height=BOARD_HEIGHT, bit_depth=4, color_order="RBG")


pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

try:
    wifi.radio.connect(SSID, PASSWORD)
    time.sleep(1) 
except OSError as e:
    print(f"OSError: {e}")

def get_clock():
    now = time.localtime()
    hour = now.tm_hour
    minute = now.tm_min
    period = "AM" if hour < 12 else "PM"
    hour_12 = hour % 12 or 12
    return f"{hour_12}:{minute:02d}{period}"

def fetch_weather():
    try:
        print("Fetching weather")
        print(f"{URL}?{WEATHER_PARAMS}")
        with requests.get(f"{URL}?{WEATHER_PARAMS}", headers={
            "X-API-Key": os.getenv("API_KEY")
        }) as response:
            print(response.json())
            json_data = response.json()
            return {
                "current_temperature": round(json_data["current_temperature"]),
                "feels_like_temperature": round(json_data["feels_like_temperature"]),
                "is_day": json_data["is_day"],
                "weather_code": json_data["weather_code"],
                "humidity": round(json_data["humidity"]),
                "min_temp": round(json_data["min_temp"]),
                "max_temp": round(json_data["max_temp"]),
                "precip_probability": round(json_data["precip_probability"]),
                "uv_index": round(json_data["uv_index"]),
                "tz_offset": json_data["tz_offset"],
            }
    except (OSError, KeyError, ValueError) as e:
        print(f"Weather fetch failed: {e}")
        return None

matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(19, 4),
    text_color=0xFFFFFF,
)
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(19, 13),
    text_color=0xFFFFFF,
)
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(64, 25),
    text_color=0xFFFFFF,
    scrolling=True,
)

def update_display(weather):
    if len(matrixportal.root_group) > 0:
        matrixportal.root_group.pop(0)
    icon = get_icon(weather["weather_code"], weather["is_day"])
    matrixportal.root_group.insert(0, icon)

    matrixportal.set_text(f"{weather['current_temperature']}F", index=1)
    matrixportal.set_text(
        f"H:{weather['max_temp']}  L:{weather['min_temp']}  UV:{weather['uv_index']}  Rain:{weather['precip_probability']}%  Humidity:{weather['humidity']}%  Feels Like:{weather['feels_like_temperature']}F",
        index=2
    )

def sync_ntp():
    synced = False
    count = 0
    while not synced and count < 10:
        try:
            rtc.RTC().datetime = ntp.datetime
            synced = True
            print("NTP synced")
        except OSError as e:
            print(f"NTP sync failed: {e}, retrying in 5s...")
            count = count + 1
            time.sleep(5)

def setup():
    weather = fetch_weather()
    tz_offset = weather["tz_offset"] if weather else -5
    global ntp
    ntp = adafruit_ntp.NTP(pool, tz_offset=tz_offset, server="time.google.com")
    sync_ntp()
    if weather:
        update_display(weather)
    else:
        matrixportal.set_text("Weather unavailable", index=2)
    current_time = get_clock()
    matrixportal.set_text(current_time, index=0)
    return current_time

ntp = None
last_displayed_time = setup()


WEATHER_REFRESH_INTERVAL = 300  # 5 minutes
CLOCK_REFRESH_INTERVAL = 1
NTP_SYNC_INTERVAL = 86400  # 24 hours in seconds

last_weather_refresh = time.monotonic()
last_clock_refresh = time.monotonic()
last_ntp_sync = time.monotonic()

while True:
    if time.monotonic() - last_weather_refresh >= WEATHER_REFRESH_INTERVAL:
        weather = fetch_weather()
        if weather:
            update_display(weather)
        last_weather_refresh = time.monotonic()

    if time.monotonic() - last_clock_refresh >= CLOCK_REFRESH_INTERVAL:
        current_time = get_clock()
        if current_time != last_displayed_time:
            matrixportal.set_text(current_time, index=0)
            last_displayed_time = current_time
        last_clock_refresh = time.monotonic()
    if time.monotonic() - last_ntp_sync >= NTP_SYNC_INTERVAL:
        sync_ntp()
        last_ntp_sync = time.monotonic()
    matrixportal.scroll()
    time.sleep(0.04)
