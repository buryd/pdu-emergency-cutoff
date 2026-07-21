"""Virtual hardware for the PDU Emergency Cutoff System.

Models every physical device the firmware touches:

- CT primary current  : a settable amps value ("what the clamp sees")
- SCT-013-005 + bias  : synthesizes the 60 Hz AC waveform riding on the
                        ADC_VREF/2 DC bias, scaled with the same
                        AMPS_PER_ADC_VOLT constant the firmware uses
- Pico ADC            : adc_read_u16() returns that waveform as counts
- DLI IoT Power Relay : watches the trip GPIO; Normally On opens when the
                        trip level is asserted, which also collapses the
                        measured current to 0 A (PDU is dead)
- Pushbuttons         : press_button() holds the pin low briefly
- LEDs                : levels recorded from firmware writes

The real firmware/config.py is imported, so pin numbers, polarity, and
scaling always match the design.
"""

import math
import threading
import time

import config as cfg

_BUTTON_HOLD_S = 0.4
_MAINS_HZ = 60.0

# time.monotonic() can have ~15.6 ms resolution on Windows, which is far
# too coarse to synthesize a 60 Hz waveform; perf_counter is always high-res.
_now = time.perf_counter


class VirtualWorld:
    def __init__(self):
        self._lock = threading.RLock()
        self.set_amps = cfg.DEFAULT_BASELINE_AMPS
        self.relay_on = True          # DLI "Normally On" energized
        self.trip_pin_level = None    # last level firmware wrote on GP15
        self.verbose = True
        self._pressed_until = {}      # gpio -> monotonic deadline
        self.led_levels = {}          # gpio -> 0/1
        self._led_names = {
            cfg.PIN_LED_ARMED: "ARMED",
            cfg.PIN_LED_TRIPPED: "TRIPPED",
            cfg.PIN_LED_LEARN: "LEARN",
        }
        self._btn_pins = {
            "learn": cfg.PIN_BTN_LEARN,
            "save": cfg.PIN_BTN_SAVE,
            "reset": cfg.PIN_BTN_RESET,
        }

    # --- CT primary / operator controls ---

    def set_current(self, amps):
        with self._lock:
            self.set_amps = max(0.0, float(amps))

    def press_button(self, name, hold_s=_BUTTON_HOLD_S):
        gpio = self._btn_pins[name]
        self._pressed_until[gpio] = _now() + hold_s

    # --- CT secondary -> bias adapter -> ADC ---

    def effective_amps(self):
        """Current actually flowing: 0 A once the relay cuts the PDU."""
        with self._lock:
            return self.set_amps if self.relay_on else 0.0

    def adc_read_u16(self):
        amps = self.effective_amps()
        v_rms = amps / cfg.AMPS_PER_ADC_VOLT
        v = 0.5 * cfg.ADC_VREF + v_rms * math.sqrt(2) * math.sin(
            2 * math.pi * _MAINS_HZ * _now()
        )
        v = min(max(v, 0.0), cfg.ADC_VREF)
        return int(v / cfg.ADC_VREF * 65535)

    # --- GPIO seen by the mock machine module ---

    def read_pin(self, gpio):
        deadline = self._pressed_until.get(gpio)
        if deadline is not None and _now() < deadline:
            return 0
        return 1

    def write_pin(self, gpio, value):
        if gpio == cfg.PIN_TRIP:
            self._on_trip_write(value)
        elif gpio in self._led_names:
            self.led_levels[gpio] = value

    def _on_trip_write(self, value):
        cut = (value == 0) if cfg.TRIP_ACTIVE_LOW else (value == 1)
        with self._lock:
            self.trip_pin_level = value
            changed = self.relay_on == cut
            self.relay_on = not cut
        if changed and self.verbose:
            if cut:
                print("[DLI] Trip asserted -> Normally On OPEN, PDU is OFF")
            else:
                print("[DLI] Trip released -> Normally On CLOSED, PDU is ON")

    # --- Introspection ---

    def status(self):
        with self._lock:
            return {
                "ct_primary_set_amps": self.set_amps,
                "ct_primary_effective_amps": self.effective_amps(),
                "dli_normally_on": self.relay_on,
                "trip_pin_level": self.trip_pin_level,
                "leds": {
                    name: self.led_levels.get(gpio, 0)
                    for gpio, name in self._led_names.items()
                },
            }


WORLD = VirtualWorld()
