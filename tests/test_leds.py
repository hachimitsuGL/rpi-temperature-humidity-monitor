import unittest

from climate_monitor.leds import LedController
from climate_monitor.config import LED_PINS


class FakeGPIO:
    OUT, LOW, HIGH = "out", 0, 1

    def __init__(self):
        self.outputs = {}

    def setup(self, pin, mode, initial):
        self.outputs[pin] = initial

    def output(self, pin, value):
        self.outputs[pin] = value


class LedTests(unittest.TestCase):
    def test_two_leds_and_clear(self):
        gpio = FakeGPIO()
        leds = LedController(gpio)
        leds.show({"blue", "white"})
        self.assertEqual(gpio.outputs[LED_PINS["blue"]], gpio.HIGH)
        self.assertEqual(gpio.outputs[LED_PINS["white"]], gpio.HIGH)
        self.assertEqual(gpio.outputs[LED_PINS["red"]], gpio.LOW)
        leds.off()
        self.assertTrue(all(value == gpio.LOW for value in gpio.outputs.values()))


if __name__ == "__main__":
    unittest.main()
