"""Hardware wiring and default application settings (BCM pin numbering)."""

# Temperature/humidity sampling
DHT_GPIO = 4
SAMPLE_INTERVAL_SECONDS = 5
HISTORY_MAX_POINTS = 360  # ~30 minutes at one reading per 5 seconds

# SSD1306 OLED over I2C
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_I2C_ADDRESSES = (0x3C, 0x3D)

# Five LEDs
LED_PINS = {
    "blue": 26,
    "white": 19,
    "green": 13,
    "yellow": 21,
    "red": 20,
}

# Switch 1 changes the setting; switch 2 increases, switch 3 decreases.
SWITCH_PINS = (6, 5, 12)
EDIT_TIMEOUT_SECONDS = 5
BUTTON_BOUNCE_MILLISECONDS = 200

DEFAULT_COMFORT = {"min_t": 20, "max_t": 25, "min_h": 45, "max_h": 60}

WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
