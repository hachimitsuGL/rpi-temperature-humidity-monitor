"""Hardware startup, sampling loop, and shutdown."""

import threading
import time

from .buttons import ButtonController
from .config import SAMPLE_INTERVAL_SECONDS, WEB_HOST, WEB_PORT
from .display import OledDisplay
from .leds import LedController
from .logic import classify
from .sensor import DHT11Sensor
from .settings import ComfortSettings
from .state import MonitorState
from .web import create_app, get_local_ip


def main():
    # Delayed hardware import allows logic and HTTP tests to run on a Mac/PC.
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    display = None
    sensor = None
    buttons = None
    leds = None

    settings = ComfortSettings()
    state = MonitorState()

    try:
        display = OledDisplay()
        display.show_lines("INIT", "READY")
        time.sleep(1)

        sensor = DHT11Sensor()
        leds = LedController(GPIO)
        buttons = ButtonController(GPIO, display, settings)
        buttons.start()

        app = create_app(state, settings)
        server = threading.Thread(
            target=lambda: app.run(
                host=WEB_HOST, port=WEB_PORT, debug=False, use_reloader=False
            ),
            daemon=True,
            name="flask-server",
        )
        server.start()
        print(f"Web monitor: http://{get_local_ip()}:{WEB_PORT}")

        while True:
            # As in the original program, sampling pauses in edit mode.
            if buttons.is_normal:
                try:
                    temperature, humidity = sensor.read()
                    reading = classify(temperature, humidity, settings.snapshot())
                    leds.show(reading.led_colors)
                    state.update(temperature, humidity,
                                 reading.temp_status, reading.hum_status)
                    display.show_lines(
                        f"温度 {temperature:.1f}℃",
                        f"湿度 {humidity:.1f}%",
                        reading.temp_status,
                        reading.hum_status,
                    )
                    print(f"現在の温度: {temperature:.1f} °C")
                    print(f"現在の湿度: {humidity:.1f} %RH")
                    print("-" * 20)
                except RuntimeError as exc:
                    # Transient DHT11 failures are common; retry next cycle.
                    print(f"retrying: {exc}")
                    display.show_lines("DHT ERR", "RETRY")
            time.sleep(SAMPLE_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        if display is not None:
            display.show_lines("STOP", "")
    finally:
        if buttons is not None:
            buttons.stop()
        if sensor is not None:
            sensor.close()
        if leds is not None:
            leds.off()
        if display is not None:
            display.clear()
        GPIO.cleanup()
