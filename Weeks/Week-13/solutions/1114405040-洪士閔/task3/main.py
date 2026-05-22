from machine import Pin, I2C
import framebuf
import math
import sh1107
import time

# ESP32 I2C pin assignment for SSD1306
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

FONT_3X5 = {
    "A": ("111", "101", "111", "101", "101"),
    "C": ("111", "100", "100", "100", "111"),
    "E": ("111", "100", "110", "100", "111"),
    "F": ("111", "100", "110", "100", "100"),
    "I": ("111", "010", "010", "010", "111"),
    "S": ("111", "100", "111", "001", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "0": ("111", "101", "101", "101", "111"),
    "6": ("111", "100", "111", "101", "111"),
    " ": ("000", "000", "000", "000", "000"),
    "?": ("111", "001", "011", "000", "010"),
}

# Chinese 32x32 dot matrix data
FONT_82B1 = bytearray(
    b'\x00\x00\x00\x00\x00\x7c\x1e\x00\x00\x78\x1c\x10'
    b'\x00\x78\x1c\x18\x00\x78\x1c\x3c\x7f\xff\xff\xfe'
    b'\x00\x78\x1c\x00\x00\x78\x1c\x00\x00\x78\x1c\x00'
    b'\x00\x00\x00\x00\x00\xf0\xf8\x00\x00\xf8\xf0\x00'
    b'\x01\xf0\xf0\x70\x01\xe0\xf0\xf8\x03\xc0\xf1\xf0'
    b'\x03\xc0\xf1\xe0\x07\xe0\xf3\xc0\x0f\xe0\xf7\x00'
    b'\x0d\xe0\xfc\x00\x19\xe0\xf0\x00\x31\xe0\xf0\x00'
    b'\x41\xe0\xf0\x00\x01\xe0\xf0\x04\x01\xe0\xf0\x04'
    b'\x01\xe0\xf0\x04\x01\xe0\xf0\x0c\x01\xe0\xf0\x0c'
    b'\x01\xe0\xff\xfe\x01\xe0\xff\xfe\x01\xe0\x7f\xfe'
    b'\x01\xc0\x0f\xe0\x00\x00\x00\x00'
)

FONT_706B = bytearray(
    b'\x00\x00\x00\x00\x00\x07\x00\x00\x00\x07\x80\x00'
    b'\x00\x07\x80\x00\x00\x07\x80\x00\x00\x07\x80\x00'
    b'\x00\x07\x80\x00\x01\x07\x80\x60\x01\x07\x80\xf0'
    b'\x01\x87\xc0\xfc\x01\x87\xc1\xf0\x03\x87\xc3\xe0'
    b'\x03\x87\xc3\xc0\x07\x8f\x47\x00\x0f\x8f\x6e\x00'
    b'\x1f\x0f\x68\x00\x1f\x0f\x30\x00\x1e\x0f\x30\x00'
    b'\x00\x1e\x30\x00\x00\x1e\x38\x00\x00\x1e\x1c\x00'
    b'\x00\x3c\x1e\x00\x00\x38\x1e\x00\x00\x78\x0f\x80'
    b'\x00\xf0\x0f\xc0\x01\xe0\x07\xf0\x03\xc0\x03\xfc'
    b'\x07\x00\x01\xfe\x0e\x00\x00\xf8\x18\x00\x00\x70'
    b'\x40\x00\x00\x10\x00\x00\x00\x00'
)

FONT_7BC0 = bytearray(
    b'\x07\x80\x38\x00\x07\x84\x7c\x18\x07\x0e\x78\x3c'
    b'\x0f\xff\x7f\xfe\x0e\xe0\xe7\x00\x1c\x70\xc3\x80'
    b'\x18\x71\x83\xc0\x30\x71\x03\xc0\x60\x74\x01\x90'
    b'\x0c\x0e\x38\x38\x0f\xff\x3f\xfc\x0e\x0f\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0f\xff\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0f\xff\x38\x3c\x0e\x0e\x38\x3c'
    b'\x0e\x20\x38\x3c\x0e\x38\x38\x3c\x0e\x1c\x38\xf8'
    b'\x0e\x1e\x38\x78\x1f\xff\x38\x78\x7f\xc7\x38\x60'
    b'\x7f\x07\x38\x00\x3c\x07\x38\x00\x20\x00\x38\x00'
    b'\x00\x00\x30\x00\x00\x00\x00\x00'
)

CHARS = {
    "花": (FONT_82B1, 32, 32),
    "火": (FONT_706B, 32, 32),
    "節": (FONT_7BC0, 32, 32),
}


def draw_tiny_text(display, text, x, y, scale=1, spacing=1, color=1):
    cursor_x = x
    for ch in text.upper():
        glyph = FONT_3X5.get(ch, FONT_3X5["?"])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit != "1":
                    continue
                px = cursor_x + col * scale
                py = y + row * scale
                if scale == 1:
                    display.pixel(px, py, color)
                else:
                    display.fill_rect(px, py, scale, scale, color)
        cursor_x += (3 * scale) + spacing


def draw_circle(display, cx, cy, r, color=1):
    x = r
    y = 0
    err = 0
    while x >= y:
        display.pixel(cx + x, cy + y, color)
        display.pixel(cx + y, cy + x, color)
        display.pixel(cx - y, cy + x, color)
        display.pixel(cx - x, cy + y, color)
        display.pixel(cx - x, cy - y, color)
        display.pixel(cx - y, cy - x, color)
        display.pixel(cx + y, cy - x, color)
        display.pixel(cx + x, cy - y, color)
        y += 1
        if err <= 0:
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1


def draw_star_polygon(display, cx, cy, size, angle, color=1):
    points = []
    for i in range(5):
        theta = angle + i * (2 * math.pi / 5)
        points.append((cx + int(math.cos(theta) * size), cy + int(math.sin(theta) * size)))

    for i in range(5):
        x1, y1 = points[i]
        x2, y2 = points[(i + 2) % 5]
        display.line(x1, y1, x2, y2, color)


def draw_rotating_star(display, cx, cy, base_size, angle, breathing, color=1):
    outer_size = max(4, int(base_size * breathing))
    inner_size = max(3, int((base_size - 2) * breathing))
    draw_star_polygon(display, cx, cy, outer_size, angle, color)
    draw_star_polygon(display, cx, cy, inner_size, -angle * 1.2, color)
    display.pixel(cx, cy, color)


def draw_orbit_sparks(display, cx, cy, radius, frame_idx, color=1):
    for idx in range(12):
        theta = frame_idx * 0.16 + idx * (2 * math.pi / 12)
        spark_r = radius + (1 if idx % 3 == 0 else 0)
        x = cx + int(math.cos(theta) * spark_r)
        y = cy + int(math.sin(theta) * spark_r)
        display.pixel(x, y, color)
        if idx % 2 == 0:
            display.pixel(x + 1, y, color)


def draw_char(display, char, x, y, shrink=1):
    if char not in CHARS:
        return

    data, w, h = CHARS[char]
    fb = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)

    if shrink <= 1:
        display.blit(fb, x, y)
        return

    out_w = (w + shrink - 1) // shrink
    out_h = (h + shrink - 1) // shrink
    for oy in range(out_h):
        sy = oy * shrink
        for ox in range(out_w):
            sx = ox * shrink
            if fb.pixel(sx, sy):
                display.pixel(x + ox, y + oy, 1)


def draw_text_vertical_flash(display, text, x, y, frame_idx, spacing=1):
    cy = y
    for idx, ch in enumerate(text):
        phase = frame_idx * 0.18 + idx * 0.8
        flash_on = math.sin(phase) > -0.15
        shrink = 1 if flash_on else 2
        draw_char(display, ch, x, cy, shrink=shrink)
        _, _, h = CHARS[ch]
        cy += ((h + shrink - 1) // shrink) + spacing


def draw_text_wave(display, text, x, y, frame_idx):
    cursor_x = x
    for idx, ch in enumerate(text):
        phase = frame_idx * 0.22 + idx * 0.9
        wave_y = y + int(math.sin(phase) * 3)
        scale = 1 + int((math.sin(phase) + 1) * 0.5)
        draw_tiny_text(display, ch, cursor_x, wave_y, scale=scale, spacing=1)
        cursor_x += 8


def render_frame(frame_idx):
    oled.fill(0)

    oled.rect(0, 0, 128, 64, 1)
    draw_tiny_text(oled, "PENGHU", 2, 2, scale=1)
    draw_tiny_text(oled, "CSIE", 2, 10, scale=1)
    draw_tiny_text(oled, "WOKWI", 2, 18, scale=1)

    cx = 62
    cy = 32
    breathing = 1.0 + 0.12 * math.sin(frame_idx * 0.14)
    angle = frame_idx * 0.18

    draw_circle(oled, cx, cy, 22, 1)
    draw_circle(oled, cx, cy, 23, 1)
    draw_orbit_sparks(oled, cx, cy, 26, frame_idx, 1)
    draw_rotating_star(oled, cx, cy, 8, angle, breathing, 1)

    oled.text("2026", 90, 2)
    draw_text_vertical_flash(oled, "花火節", 99, 12, frame_idx, spacing=1)
    draw_text_wave(oled, "CSIE", 18, 49, frame_idx)
    draw_tiny_text(oled, "SHINE", 79, 54, scale=1)

    oled.show()


frame_idx = 0
while True:
    render_frame(frame_idx)
    frame_idx += 1
    time.sleep(0.08)
