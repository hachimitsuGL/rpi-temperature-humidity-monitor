import unittest

from climate_monitor.buttons import ButtonController
from climate_monitor.settings import ComfortSettings


class FakeGPIO:
    IN, PUD_UP, FALLING = "in", "up", "falling"

    def __init__(self):
        self.callbacks = {}

    def setup(self, pin, mode, pull_up_down=None):
        pass

    def add_event_detect(self, pin, edge, callback, bouncetime):
        self.callbacks[pin] = callback

    def remove_event_detect(self, pin):
        self.callbacks.pop(pin)

    def press(self, pin):
        self.callbacks[pin](pin)


class FakeDisplay:
    def show_lines(self, *args, **kwargs):
        pass

    def show_adjust(self, *args, **kwargs):
        pass


class ButtonTests(unittest.TestCase):
    def test_switch_cycle_and_adjustment(self):
        gpio = FakeGPIO()
        settings = ComfortSettings()
        controller = ButtonController(gpio, FakeDisplay(), settings)
        controller.start()
        try:
            self.assertTrue(controller.is_normal)
            gpio.press(6)  # max_t
            gpio.press(5)  # +1
            self.assertEqual(settings.snapshot().max_t, 26)
            gpio.press(6)  # min_t
            gpio.press(12)  # -1
            self.assertEqual(settings.snapshot().min_t, 19)
            gpio.press(6)  # max_h
            gpio.press(6)  # min_h
            gpio.press(6)  # normal
            self.assertTrue(controller.is_normal)
            gpio.press(5)  # +/- inactive during normal monitoring
            self.assertEqual(settings.snapshot().max_t, 26)
        finally:
            controller.stop()
        self.assertFalse(gpio.callbacks)


if __name__ == "__main__":
    unittest.main()
