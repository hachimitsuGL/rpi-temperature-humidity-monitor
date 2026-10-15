import unittest

from climate_monitor.state import MonitorState


class StateTests(unittest.TestCase):
    def test_empty_reading(self):
        state = MonitorState()
        self.assertIsNone(state.current()["temperature"])
        self.assertEqual(state.history(), [])

    def test_history_limit(self):
        state = MonitorState(max_points=2)
        for t in (20, 21, 22):
            state.update(t, 50, "comfortable", "comfortable")
        self.assertEqual([item["temperature"] for item in state.history()], [21, 22])
        self.assertEqual(state.current()["temperature"], 22)


if __name__ == "__main__":
    unittest.main()
