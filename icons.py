import displayio

BITMAP_SIZE = 16

def draw_sun():
    bitmap = displayio.Bitmap(BITMAP_SIZE, BITMAP_SIZE, 3)
    palette = displayio.Palette(3)
    palette[0] = 0x000000
    palette[1] = 0xFFD700  # gold
    palette[2] = 0xFFF176  # pale yellow glint

    # cardinal rays
    for i in range(7, 9):
        bitmap[i, 0] = 1
        bitmap[i, 1] = 1
        bitmap[i, 14] = 1
        bitmap[i, 15] = 1
        bitmap[0, i] = 1
        bitmap[1, i] = 1
        bitmap[14, i] = 1
        bitmap[15, i] = 1

    # diagonal rays
    bitmap[2, 2] = 1
    bitmap[3, 3] = 1
    bitmap[12, 2] = 1
    bitmap[13, 3] = 1
    bitmap[2, 13] = 1
    bitmap[3, 12] = 1
    bitmap[12, 13] = 1
    bitmap[13, 12] = 1

    # sun body
    for x in range(5, 11):
        bitmap[x, 4] = 1
        bitmap[x, 11] = 1
    for y in range(4, 12):
        bitmap[4, y] = 1
        bitmap[11, y] = 1
        for x in range(5, 11):
            bitmap[x, y] = 1

    # glint
    bitmap[6, 5] = 2
    bitmap[7, 5] = 2
    bitmap[6, 6] = 2

    return displayio.TileGrid(bitmap, pixel_shader=palette)

def draw_moon():
    bitmap = displayio.Bitmap(BITMAP_SIZE, BITMAP_SIZE, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000
    palette[1] = 0xC8D8E8

    moon_pixels = [
        "0001111110000000",
        "0011111111000000",
        "0111111111100000",
        "1111111111110000",
        "1111111111110000",
        "1111111111110000",
        "1111111111110000",
        "1111111111110000",
        "1111111111110000",
        "1111111111110000",
        "0111111111100000",
        "0011111111000000",
        "0001111110000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
    ]
    cut = [
        "0000000000000000",
        "0000000111000000",
        "0000001111100000",
        "0000011111110000",
        "0000011111110000",
        "0000011111110000",
        "0000011111110000",
        "0000011111110000",
        "0000011111110000",
        "0000011111110000",
        "0000001111100000",
        "0000000111000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
    ]
    for y in range(BITMAP_SIZE):
        for x in range(BITMAP_SIZE):
            if moon_pixels[y][x] == "1" and cut[y][x] == "0":
                bitmap[x, y] = 1

    return displayio.TileGrid(bitmap, pixel_shader=palette)

def draw_cloud():
    bitmap = displayio.Bitmap(BITMAP_SIZE, BITMAP_SIZE, 3)
    palette = displayio.Palette(3)
    palette[0] = 0x000000
    palette[1] = 0xAAAAAA  # base cloud
    palette[2] = 0xDDDDDD  # highlight

    cloud = [
        "0000111000000000",
        "0001111100000000",
        "0011222110000000",
        "0111222111100000",
        "1111111111110000",
        "1111111111110000",
        "0111111111100000",
        "0001111110000000",
    ]
    y_offset = (BITMAP_SIZE - len(cloud)) // 2
    for row_idx, row in enumerate(cloud):
        for col_idx, pixel in enumerate(row):
            if pixel == "1":
                bitmap[col_idx, y_offset + row_idx] = 1
            elif pixel == "2":
                bitmap[col_idx, y_offset + row_idx] = 2

    return displayio.TileGrid(bitmap, pixel_shader=palette)

def draw_rain():
    bitmap = displayio.Bitmap(BITMAP_SIZE, BITMAP_SIZE, 3)
    palette = displayio.Palette(3)
    palette[0] = 0x000000
    palette[1] = 0x888888  # dark cloud
    palette[2] = 0x4488FF  # blue rain

    rain = [
        "0000111000000000",
        "0001111100000000",
        "0011111110000000",
        "0111111111100000",
        "1111111111110000",
        "0111111111100000",
        "0000000000000000",
        "0020020020000000",
        "0002002002000000",
        "0020020020000000",
        "0002002002000000",
    ]
    y_offset = (BITMAP_SIZE - len(rain)) // 2
    for row_idx, row in enumerate(rain):
        for col_idx, pixel in enumerate(row):
            if pixel == "1":
                bitmap[col_idx, y_offset + row_idx] = 1
            elif pixel == "2":
                bitmap[col_idx, y_offset + row_idx] = 2

    return displayio.TileGrid(bitmap, pixel_shader=palette)

def draw_snow():
    bitmap = displayio.Bitmap(BITMAP_SIZE, BITMAP_SIZE, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000
    palette[1] = 0xDDEEFF

    snowflake = [
        "0000010100000000",
        "0000111110000000",
        "0001010100100000",
        "0100010100010000",
        "0011111111100000",
        "0001010101000000",
        "1111101011111000",
        "0001010101000000",
        "0011111111100000",
        "0100010100010000",
        "0001010100100000",
        "0000111110000000",
        "0000010100000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
    ]

    for y in range(BITMAP_SIZE):
        for x in range(BITMAP_SIZE):
            if snowflake[y][x] == "1":
                bitmap[x, y] = 1

    return displayio.TileGrid(bitmap, pixel_shader=palette)

def draw_storm():
    bitmap = displayio.Bitmap(BITMAP_SIZE, BITMAP_SIZE, 4)
    palette = displayio.Palette(4)
    palette[0] = 0x000000
    palette[1] = 0x666666  # dark cloud
    palette[2] = 0x4488FF  # rain
    palette[3] = 0xFFE033  # lightning

    storm = [
        "0000111000000000",
        "0001111100000000",
        "0011111110000000",
        "0111111111100000",
        "1111111111110000",
        "0111111111100000",
        "0002033300000000",  # rain + lightning start
        "0000033000000000",
        "0000330000000000",
        "0000033000000000",
        "0002000200000000",
    ]
    y_offset = (BITMAP_SIZE - len(storm)) // 2
    for row_idx, row in enumerate(storm):
        for col_idx, pixel in enumerate(row):
            if pixel == "1":
                bitmap[col_idx, y_offset + row_idx] = 1
            elif pixel == "2":
                bitmap[col_idx, y_offset + row_idx] = 2
            elif pixel == "3":
                bitmap[col_idx, y_offset + row_idx] = 3

    return displayio.TileGrid(bitmap, pixel_shader=palette)

def get_icon(weather_code, is_day):
    if weather_code == 0:
        return draw_sun() if is_day else draw_moon()
    elif weather_code in (1, 2, 3):
        return draw_cloud()
    elif 51 <= weather_code <= 67 or 80 <= weather_code <= 82:
        return draw_rain()
    elif 71 <= weather_code <= 77:
        return draw_snow()
    elif weather_code >= 95:
        return draw_storm()
    else:
        return draw_cloud()