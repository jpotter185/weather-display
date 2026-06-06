# Matrix Portal Weather Display

A CircuitPython weather display for the [Adafruit Matrix Portal S3](https://www.adafruit.com/product/5778) and a 64x32 RGB LED matrix. Shows current weather conditions, temperature, and a scrolling ticker with detailed weather info.

## Features

- Current temperature and weather icon (sun, moon, cloud, rain, snow, storm)
- Scrolling ticker with high/low temps, UV index, precipitation chance, humidity, and feels like temperature
- 12-hour clock synced via NTP
- Auto-detects timezone from weather API — no hardcoded offsets
- Weather refreshes every 5 minutes, clock checks every 5 seconds, NTP re-syncs every 24 hours

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

3. Create a `settings.toml` file on the `CIRCUITPY` drive with your credentials:

   ```toml
   CIRCUITPY_WIFI_SSID = "your_wifi_ssid"
   CIRCUITPY_WIFI_PASSWORD = "your_wifi_password"
   OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
   LATITUDE = "123.4"
   LONGITUDE = "567.8"
   ```

4. The board will auto-reload and start displaying weather.

## Weather API

Uses [Open-Meteo](https://open-meteo.com/) — free, no API key required.

## Project Structure

```
code.py       # main application
icons.py      # pixel art weather icon drawing functions
```
