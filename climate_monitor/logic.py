"""Pure logic for classifying readings and choosing LED colors."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReadingStatus:
    temp_status: str
    hum_status: str
    led_colors: frozenset[str]


def classify(temperature, humidity, comfort):
    """Match the original status / color behavior.

    If both temperature and humidity are outside their comfort ranges,
    two LEDs may be illuminated simultaneously.
    """
    colors = set()
    if temperature < comfort.min_t:
        temp_status = "cold"
        colors.add("blue")
    elif temperature > comfort.max_t:
        temp_status = "hot"
        colors.add("red")
    else:
        temp_status = "comfortable"

    if humidity < comfort.min_h:
        hum_status = "dry"
        colors.add("white")
    elif humidity > comfort.max_h:
        hum_status = "humid"
        colors.add("yellow")
    else:
        hum_status = "comfortable"

    if not colors:
        colors.add("green")

    return ReadingStatus(temp_status, hum_status, frozenset(colors))
