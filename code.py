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
URL = os.getenv("OPEN_METEO_URL")
WEATHER_PARAMS = (
    f"latitude={os.getenv('LATITUDE')}"
    f"&longitude={os.getenv('LONGITUDE')}"
    f"&current=temperature_2m,apparent_temperature,is_day,weather_code,relative_humidity_2m"
    f"&daily=temperature_2m_max,temperature_2m_min"
    f"&hourly=uv_index,precipitation_probability"
    f"&timezone=auto"
    f"&forecast_days=1"
    f"&wind_speed_unit=mph"
    f"&temperature_unit=fahrenheit"
    f"&precipitation_unit=inch"
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
        with requests.get(f"{URL}?{WEATHER_PARAMS}") as response:
            print("Fetched weather")
            json_data = response.json()
            current = json_data["current"]
            daily = json_data["daily"]
            hourly = json_data["hourly"]
            current_hour = int(current["time"][11:13])
            return {
                "current_temperature": round(current["temperature_2m"]),
                "feels_like_temperature": round(current["apparent_temperature"]),
                "is_day": current["is_day"],
                "weather_code": current["weather_code"],
                "humidity": round(current["relative_humidity_2m"]),
                "min_temp": round(daily["temperature_2m_min"][0]),
                "max_temp": round(daily["temperature_2m_max"][0]),
                "precip_probability": round(hourly["precipitation_probability"][current_hour]),
                "uv_index": round(hourly["uv_index"][current_hour]),
                "tz_offset": json_data["utc_offset_seconds"] // 3600,
            }
    except OSError as e:
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
    while not synced:
        try:
            rtc.RTC().datetime = ntp.datetime
            synced = True
            print("NTP synced")
        except OSError as e:
            print(f"NTP sync failed: {e}, retrying in 5s...")
            time.sleep(5)

def setup():
    weather = fetch_weather()
    tz_offset = weather["tz_offset"] if weather else -5
    global ntp
    ntp = adafruit_ntp.NTP(pool, tz_offset=tz_offset, server="time.google.com")
    sync_ntp()
    if weather:
        update_display(weather)
        current_time = get_clock()
        matrixportal.set_text(current_time, index=0)
        return current_time
    return None

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
