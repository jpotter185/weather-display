# Matrix Portal Weather Display

A CircuitPython weather display for the [Adafruit Matrix Portal S3](https://www.adafruit.com/product/5778) and a 64x32 RGB LED matrix. Shows current weather conditions, temperature, and a scrolling ticker with detailed weather info.

## Features

- Current temperature and weather icon (sun, moon, cloud, rain, snow, storm)
- Scrolling ticker with high/low temps, UV index, precipitation chance, humidity, and feels like temperature
- 12-hour clock synced via NTP
- Auto-detects timezone from weather API — no hardcoded offsets
- Weather refreshes every 5 minutes, clock checks every second, NTP re-syncs every 24 hours (and whenever the UTC offset changes, e.g. DST)
- Self-recovering: reconnects Wi-Fi, retries failed fetches every 30s, resets after ~5 min of failures, and a hardware watchdog resets the board if it hangs
- Works with CircuitPython's [web workflow](https://docs.circuitpython.org/en/latest/docs/workflows.html#web): set `CIRCUITPY_WEB_API_PASSWORD` in `settings.toml` to get a browser console/file editor at `http://<board-ip>/`. After a watchdog reset the web workflow doesn't start, so `code.py` does one extra software reset to bring it back

## Display Layout

Looks much more compact than this on the 64x32 matrix

```
+----------------------------------------------------------------+
|  [icon]                                10:45PM                 |
|                                        78F                     |
|                                                                |
| H:88  L:62  UV:0  Rain:1%  Humidity:41%  Feels Like:75F >>     |
+----------------------------------------------------------------+
```

## Hardware

- Adafruit Matrix Portal S3
- 64x32 RGB LED matrix panel

## Dependencies

Install these libraries to the `lib/` folder on your `CIRCUITPY` drive. All are available in the [Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases):

- `adafruit_matrixportal`
- `adafruit_requests`
- `adafruit_connection_manager`
- `adafruit_ntp`

## Setup

1. Clone this repo on your computer:

   ```bash
   git clone <your-repo-url>
   cd <your-repo>
   ```

2. Copy `code.py` and `icons.py` to the root of your `CIRCUITPY` drive:

   ```bash
   cp code.py icons.py /Volumes/CIRCUITPY/
   ```

3. Copy `settings.toml.example` to `settings.toml` on the `CIRCUITPY` drive and fill in your values:

   ```toml
   CIRCUITPY_WIFI_SSID = "your_wifi_ssid"
   CIRCUITPY_WIFI_PASSWORD = "your_wifi_password"
   WEATHER_API_URL = "https://your-weather-api.example.com/weather"
   API_KEY = "your_api_key"
   LATITUDE = "12.34"
   LONGITUDE = "-56.78"
   ```

   `settings.toml` is gitignored — never commit it.

4. The board will auto-reload and start displaying weather.

## Weather API

`code.py` sends `GET {WEATHER_API_URL}?lat=...&lon=...` with an `X-API-Key` header and expects JSON like:

```json
{
  "current_temperature": 61.2,
  "feels_like_temperature": 60.8,
  "is_day": 0,
  "weather_code": 63,
  "humidity": 95,
  "min_temp": 60,
  "max_temp": 65,
  "precip_probability": 61,
  "uv_index": 0,
  "tz_offset": -5
}
```

`weather_code` uses WMO codes and `tz_offset` is whole hours from UTC.

## Project Structure

```
code.py               # main application
icons.py              # pixel art weather icon drawing functions
settings.toml.example # template for the device's settings.toml
```
