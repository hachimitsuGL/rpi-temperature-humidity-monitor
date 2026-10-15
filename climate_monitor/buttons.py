"""Three physical switches for adjusting comfort ranges on the OLED."""

import threading

from .config import (
    BUTTON_BOUNCE_MILLISECONDS,
    EDIT_TIMEOUT_SECONDS,
    SWITCH_PINS,
)

# Original switch order: maximum temperature -> minimum temperature ->
# maximum humidity -> minimum humidity -> normal monitoring.
EDIT_FIELDS = (
    ("max_t", "最大温度", "℃"),
    ("min_t", "最小温度", "℃"),
    ("max_h", "最大湿度", "%"),
    ("min_h", "最小湿度", "%"),
)


class ButtonController:
    def __init__(self, gpio, display, settings):
        self._gpio = gpio
        self._display = display
        self._settings = settings
        self._lock = threading.RLock()
        self._mode = 0
        self._timer = None
        self._timer_version = 0
        self._blink_thread = None
        self._blink_stop = None
        self._started = False

    @property
    def is_normal(self):
        return self._mode == 0

    def start(self):
        if self._started:
            return
        for pin in SWITCH_PINS:
            self._gpio.setup(pin, self._gpio.IN, pull_up_down=self._gpio.PUD_UP)
        # Register the controls only once to avoid add/remove races while
        # handling edge callbacks. +/- presses are ignored outside edit mode.
        callbacks = (self._next_mode, self._increase, self._decrease)
        for pin, callback in zip(SWITCH_PINS, callbacks):
            self._gpio.add_event_detect(
                pin,
                self._gpio.FALLING,
                callback=callback,
                bouncetime=BUTTON_BOUNCE_MILLISECONDS,
            )
        self._started = True

    def _next_mode(self, channel):
        with self._lock:
            self._mode = (self._mode + 1) % 5
            if self._mode == 0:
                self._finish_edit_locked()
            else:
                self._restart_blink_locked()
                self._reset_timer_locked()

    def _increase(self, channel):
        self._adjust(1)

    def _decrease(self, channel):
        self._adjust(-1)

    def _adjust(self, delta):
        with self._lock:
            if self._mode == 0:
                return
            field = EDIT_FIELDS[self._mode - 1][0]
            self._settings.adjust(field, delta)
            self._restart_blink_locked()
            self._reset_timer_locked()

    def _reset_timer_locked(self):
        self._timer_version += 1
        version = self._timer_version
        if self._timer is not None:
            self._timer.cancel()
        self._timer = threading.Timer(
            EDIT_TIMEOUT_SECONDS, self._on_edit_timeout, args=(version,)
        )
        self._timer.daemon = True
        self._timer.start()

    def _on_edit_timeout(self, version):
        with self._lock:
            if version == self._timer_version and self._mode != 0:
                self._finish_edit_locked()

    def _finish_edit_locked(self):
        self._mode = 0
        self._timer_version += 1
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self._stop_blink_locked()
        self._display.show_lines("", "")

    def _stop_blink_locked(self):
        if self._blink_stop is not None:
            self._blink_stop.set()
        if self._blink_thread is not None:
            self._blink_thread.join()
        self._blink_stop = None
        self._blink_thread = None

    def _restart_blink_locked(self):
        self._stop_blink_locked()
        event = threading.Event()
        self._blink_stop = event
        self._blink_thread = threading.Thread(
            target=self._blink_loop,
            args=(event,),
            daemon=True,
        )
        self._blink_thread.start()

    def _blink_loop(self, stop_event):
        while not stop_event.is_set():
            # Do not acquire self._lock in this thread: GPIO callbacks wait
            # for it to finish when switching to a different edit field.
            mode = self._mode
            if not 1 <= mode <= 4:
                return
            field, label, unit = EDIT_FIELDS[mode - 1]
            value = getattr(self._settings.snapshot(), field)
            self._display.show_adjust(label, f"{value}{unit}", visible=True)
            if stop_event.wait(1):
                return
            self._display.show_adjust(label, f"{value}{unit}", visible=False)
            if stop_event.wait(1):
                return

    def stop(self):
        if not self._started:
            return
        with self._lock:
            self._finish_edit_locked()
            for pin in SWITCH_PINS:
                try:
                    self._gpio.remove_event_detect(pin)
                except RuntimeError:
                    pass
            self._started = False
