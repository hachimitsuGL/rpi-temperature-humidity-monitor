import unittest

from climate_monitor.logic import classify
from climate_monitor.settings import ComfortSettings


class ClassificationTests(unittest.TestCase):
    def setUp(self):
        self.settings = ComfortSettings().snapshot()

    def test_both_comfortable(self):
        result = classify(23, 50, self.settings)
        self.assertEqual((result.temp_status, result.hum_status),
                         ("comfortable", "comfortable"))
        self.assertEqual(result.led_colors, frozenset({"green"}))

    def test_cold_and_dry_are_two_lights(self):
        result = classify(18, 40, self.settings)
        self.assertEqual(result.led_colors, frozenset({"blue", "white"}))

    def test_hot_and_humid_are_two_lights(self):
        result = classify(29, 65, self.settings)
        self.assertEqual(result.led_colors, frozenset({"red", "yellow"}))

    def test_inclusive_boundary(self):
        result = classify(20, 60, self.settings)
        self.assertEqual(result.led_colors, frozenset({"green"}))

    def test_updates_take_effect(self):
        settings = ComfortSettings()
        settings.adjust("max_t", -3)
        self.assertEqual(classify(23, 50, settings.snapshot()).temp_status, "hot")


if __name__ == "__main__":
    unittest.main()
