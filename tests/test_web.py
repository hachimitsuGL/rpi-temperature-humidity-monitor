import unittest

from climate_monitor.settings import ComfortSettings
from climate_monitor.state import MonitorState
try:
    from climate_monitor.web import create_app
except ModuleNotFoundError as exc:
    if exc.name != "flask":
        raise
    create_app = None


@unittest.skipIf(create_app is None, "Flask is not installed in this test environment")
class WebTests(unittest.TestCase):
    def setUp(self):
        self.state = MonitorState()
        self.settings = ComfortSettings()
        self.client = create_app(self.state, self.settings).test_client()

    def test_dashboard_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("history-chart", response.get_data(as_text=True))
        self.assertIn("static/app.js", response.get_data(as_text=True))

    def test_status_and_history(self):
        self.state.update(23.0, 48.0, "comfortable", "comfortable")
        self.settings.adjust("min_t", 1)
        status = self.client.get("/api/status").get_json()
        history = self.client.get("/api/history").get_json()
        self.assertEqual(status["min_t"], 21)
        self.assertEqual(status["temperature"], 23.0)
        self.assertEqual(len(history), 1)

    def test_static_assets(self):
        self.assertEqual(self.client.get("/static/style.css").status_code, 200)
        self.assertEqual(self.client.get("/static/app.js").status_code, 200)


if __name__ == "__main__":
    unittest.main()
