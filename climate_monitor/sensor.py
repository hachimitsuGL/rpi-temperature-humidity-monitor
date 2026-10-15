"""DHT11 access; hardware imports occur only when the sensor is initialized."""

from .config import DHT_GPIO


class DHT11Sensor:
    def __init__(self):
        import board
        import adafruit_dht

        pin = getattr(board, f"D{DHT_GPIO}")
        self._device = adafruit_dht.DHT11(pin)

    def read(self):
        # Read both values as in the original program.
        temperature = self._device.temperature
        humidity = self._device.humidity
        if temperature is None or humidity is None:
            raise RuntimeError("DHT read failed")
        return float(temperature), float(humidity)

    def close(self):
        self._device.exit()
