"""Drive the five status LEDs."""

from .config import LED_PINS


class LedController:
    def __init__(self, gpio):
        self._gpio = gpio
        for pin in LED_PINS.values():
            gpio.setup(pin, gpio.OUT, initial=gpio.LOW)

    def show(self, colors):
        for color, pin in LED_PINS.items():
            self._gpio.output(pin, self._gpio.HIGH if color in colors else self._gpio.LOW)

    def off(self):
        self.show(set())
