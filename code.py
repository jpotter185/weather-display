import time
import os
import gc
import microcontroller
import terminalio
import wifi
import rtc
import adafruit_connection_manager
import adafruit_requests
import adafruit_ntp
from watchdog import WatchDogMode
from adafruit_matrixportal.matrixportal import MatrixPortal
from icons import get_icon

SSID = os.getenv("CIRCUITPY_WIFI_SSID")
PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")
URL = os.getenv("WEATHER_API_URL")
API_KEY = os.getenv("API_KEY")
WEATHER_PARAMS = (
    f"lat={os.getenv('LATITUDE')}"
    f"&lon={os.getenv('LONGITUDE')}"
)
BOARD_WIDTH = 64
BOARD_HEIGHT = 32

WEATHER_REFRESH_INTERVAL = 300  # 5 minutes
RETRY_INTERVAL = 30  # retry sooner after a failed fetch
CLOCK_REFRESH_INTERVAL = 1
NTP_SYNC_INTERVAL = 86400  # 24 hours
REQUEST_TIMEOUT = 15
DEFAULT_TZ_OFFSET = -5
# After this many failed weather fetches in a row (~5 min at RETRY_INTERVAL),
# assume the network stack is wedged and hard-reset the board.
MAX_CONSECUTIVE_FAILURES = 10
# Hardware watchdog: if the loop stops feeding it for this long (e.g. a hung
# socket), the board resets itself instead of freezing.
WATCHDOG_TIMEOUT = 60

wdt = microcontroller.watchdog
wdt.timeout = WATCHDOG_TIMEOUT
wdt.mode = WatchDogMode.RESET

pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

matrixportal = None
current_icon = None
current_tz_offset = None


def log_exception(e):
    try:
        import traceback
        traceback.print_exception(e)
    except Exception:
        print(f"{type(e).__name__}: {e}")


def release_sockets():
    """Free any sockets left open by a failed request."""
    try:
        adafruit_connection_manager.connection_manager_close_all(pool)
    except Exception as e:
        print(f"Socket cleanup failed: {e}")
    gc.collect()


def ensure_wifi():
    if wifi.radio.connected:
        return True
    for attempt in range(1, 4):
        wdt.feed()
        try:
            print(f"Connecting to Wi-Fi (attempt {attempt})...")
            wifi.radio.connect(SSID, PASSWORD, timeout=15)
            print(f"Wi-Fi connected: {wifi.radio.ipv4_address}")
            return True
        except Exception as e:
            print(f"Wi-Fi connect failed: {e}")
            time.sleep(3)
    return False


def fetch_weather():
    if not ensure_wifi():
        return None
    response = None
    try:
        print("Fetching weather")
        response = requests.get(
            f"{URL}?{WEATHER_PARAMS}",
            headers={"X-API-Key": API_KEY},
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code != 200:
            print(f"Weather API returned HTTP {response.status_code}")
            return None
        data = response.json()
        print(data)
        return {
            "current_temperature": round(data["current_temperature"]),
            "feels_like_temperature": round(data["feels_like_temperature"]),
            "is_day": data["is_day"],
            "weather_code": data["weather_code"],
            "humidity": round(data["humidity"]),
            "min_temp": round(data["min_temp"]),
            "max_temp": round(data["max_temp"]),
            "precip_probability": round(data["precip_probability"]),
            "uv_index": round(data["uv_index"]),
            "tz_offset": data["tz_offset"],
        }
    except Exception as e:
        # Any failure here (network, bad JSON, missing/null field) just means
        # "no update this round" - never crash the display over it.
        print(f"Weather fetch failed: {type(e).__name__}: {e}")
        release_sockets()
        return None
    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass


def sync_ntp(tz_offset):
    """Set the RTC from NTP. Returns True on success."""
    global current_tz_offset
    if not ensure_wifi():
        return False
    for attempt in range(1, 6):
        wdt.feed()
        try:
            ntp = adafruit_ntp.NTP(pool, tz_offset=tz_offset, server="time.google.com")
            rtc.RTC().datetime = ntp.datetime
            current_tz_offset = tz_offset
            print(f"NTP synced (UTC{tz_offset:+})")
            return True
        except Exception as e:
            print(f"NTP sync failed ({attempt}/5): {e}")
            release_sockets()
            time.sleep(5)
    return False


def get_clock():
    now = time.localtime()
    hour = now.tm_hour
    period = "AM" if hour < 12 else "PM"
    hour_12 = hour % 12 or 12
    return f"{hour_12}:{now.tm_min:02d}{period}"


def update_display(weather):
    global current_icon
    icon = get_icon(weather["weather_code"], weather["is_day"])
    group = matrixportal.root_group
    if current_icon is not None:
        try:
            group.remove(current_icon)
        except ValueError:
            pass
    group.insert(0, icon)
    current_icon = icon

    matrixportal.set_text(f"{weather['current_temperature']}F", index=1)
    matrixportal.set_text(
        f"H:{weather['max_temp']}  L:{weather['min_temp']}  UV:{weather['uv_index']}  "
        f"Rain:{weather['precip_probability']}%  Humidity:{weather['humidity']}%  "
        f"Feels Like:{weather['feels_like_temperature']}F",
        index=2,
    )


def setup_display():
    global matrixportal
    matrixportal = MatrixPortal(
        width=BOARD_WIDTH, height=BOARD_HEIGHT, bit_depth=4, color_order="RBG"
    )
    matrixportal.add_text(text_font=terminalio.FONT, text_position=(19, 4), text_color=0xFFFFFF)
    matrixportal.add_text(text_font=terminalio.FONT, text_position=(19, 13), text_color=0xFFFFFF)
    matrixportal.add_text(
        text_font=terminalio.FONT,
        text_position=(64, 25),
        text_color=0xFFFFFF,
        scrolling=True,
    )


def main():
    setup_display()
    matrixportal.set_text("Connecting...", index=2)

    weather = fetch_weather()
    sync_ntp(weather["tz_offset"] if weather else DEFAULT_TZ_OFFSET)
    if weather:
        update_display(weather)
    else:
        matrixportal.set_text("Weather unavailable", index=2)

    last_displayed_time = get_clock()
    matrixportal.set_text(last_displayed_time, index=0)

    failures = 0 if weather else 1
    now = time.monotonic()
    next_weather = now + (WEATHER_REFRESH_INTERVAL if weather else RETRY_INTERVAL)
    last_clock_refresh = now
    last_ntp_sync = now

    while True:
        wdt.feed()
        now = time.monotonic()

        if now >= next_weather:
            weather = fetch_weather()
            if weather:
                failures = 0
                update_display(weather)
                # Re-sync if the UTC offset changed (e.g. DST)
                if weather["tz_offset"] != current_tz_offset:
                    sync_ntp(weather["tz_offset"])
                    last_ntp_sync = time.monotonic()
                next_weather = time.monotonic() + WEATHER_REFRESH_INTERVAL
            else:
                failures += 1
                print(f"Consecutive weather failures: {failures}")
                if failures >= MAX_CONSECUTIVE_FAILURES:
                    raise RuntimeError("Too many consecutive weather failures")
                next_weather = time.monotonic() + RETRY_INTERVAL

        if now - last_clock_refresh >= CLOCK_REFRESH_INTERVAL:
            current_time = get_clock()
            if current_time != last_displayed_time:
                matrixportal.set_text(current_time, index=0)
                last_displayed_time = current_time
            last_clock_refresh = now

        if now - last_ntp_sync >= NTP_SYNC_INTERVAL:
            sync_ntp(current_tz_offset if current_tz_offset is not None else DEFAULT_TZ_OFFSET)
            last_ntp_sync = time.monotonic()

        matrixportal.scroll()
        time.sleep(0.04)


try:
    main()
except Exception as e:
    # Last-resort safety net: log it, show it, then hard-reset instead of
    # sitting halted until someone power-cycles the board.
    print("Fatal error, resetting in 10s:")
    log_exception(e)
    try:
        if matrixportal is not None:
            matrixportal.set_text("Error - restarting", index=2)
    except Exception:
        pass
    for _ in range(10):
        wdt.feed()
        time.sleep(1)
    microcontroller.reset()
