"""SSD1306 OLED output with Japanese text and state icons."""

import os
import threading
import time

from .config import OLED_HEIGHT, OLED_I2C_ADDRESSES, OLED_WIDTH
from ._drawing import centered_x, draw_humidity_icon, draw_temperature_icon


FONT_CANDIDATES = (
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansJP-Bold.otf",
    "/usr/share/fonts/opentype/noto/NotoSansJP-Regular.otf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
)


def find_japanese_font():
    for candidate in FONT_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    raise RuntimeError("Japanese font not found: sudo apt install fonts-noto-cjk")


class OledDisplay:
    def __init__(self):
        import board
        import adafruit_ssd1306
        from PIL import Image, ImageDraw, ImageFont

        i2c = board.I2C()
        while not i2c.try_lock():
            time.sleep(0.01)
        try:
            detected = i2c.scan()
        finally:
            i2c.unlock()

        address = next((a for a in OLED_I2C_ADDRESSES if a in detected), None)
        if address is None:
            raise RuntimeError(f"SSD1306 not found (I2C devices: {detected})")

        self._oled = adafruit_ssd1306.SSD1306_I2C(
            OLED_WIDTH, OLED_HEIGHT, i2c, addr=address
        )
        font_path = find_japanese_font()
        self._normal_font = ImageFont.truetype(font_path, 20)
        self._title_font = ImageFont.truetype(font_path, 11)
        self._label_font = ImageFont.truetype(font_path, 18)
        self._value_font = ImageFont.truetype(font_path, 20)
        self._image = Image
        self._draw = ImageDraw
        self._lock = threading.Lock()
        self.clear()

    def clear(self):
        with self._lock:
            self._oled.fill(0)
            self._oled.show()

    def show_lines(self, line1, line2="", temp_status=None, hum_status=None):
        image = self._image.new("1", (OLED_WIDTH, OLED_HEIGHT))
        draw = self._draw.Draw(image)
        icons = temp_status is not None or hum_status is not None
        line1_y, line2_y = (12, 38) if icons else (2, 34)
        draw.text((centered_x(draw, str(line1), self._normal_font), line1_y),
                  str(line1), font=self._normal_font, fill=255)
        draw.text((centered_x(draw, str(line2), self._normal_font), line2_y),
                  str(line2), font=self._normal_font, fill=255)
        if temp_status is not None:
            draw_temperature_icon(draw, temp_status)
        if hum_status is not None:
            draw_humidity_icon(draw, hum_status)
        with self._lock:
            self._oled.image(image)
            self._oled.show()

    def show_adjust(self, label, value, visible=True):
        image = self._image.new("1", (OLED_WIDTH, OLED_HEIGHT))
        draw = self._draw.Draw(image)
        header = "快適ゾーン調整"
        draw.text((centered_x(draw, header, self._title_font), 0),
                  header, font=self._title_font, fill=255)
        if visible:
            draw.text((centered_x(draw, label, self._label_font), 16),
                      label, font=self._label_font, fill=255)
            draw.text((centered_x(draw, value, self._value_font), 39),
                      value, font=self._value_font, fill=255)
        with self._lock:
            self._oled.image(image)
            self._oled.show()
