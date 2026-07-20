"""
PDU Emergency Cutoff System — Raspberry Pi Pico (MicroPython)

Monitors PDU input current via SCT-013-005 + CT Bias Adapter.
Trips DLI IoT Power Relay switch port at 30% above baseline.
Default baseline: 0.4 A → trip at 0.52 A.
"""

import json
import math
import time

from machine import ADC, Pin
import config as cfg

# --- Hardware ---
adc = ADC(cfg.PIN_CT_ADC)
btn_learn = Pin(cfg.PIN_BTN_LEARN, Pin.IN, Pin.PULL_UP)
btn_save = Pin(cfg.PIN_BTN_SAVE, Pin.IN, Pin.PULL_UP)
btn_reset = Pin(cfg.PIN_BTN_RESET, Pin.IN, Pin.PULL_UP)
trip = Pin(cfg.PIN_TRIP, Pin.OUT)
led_armed = Pin(cfg.PIN_LED_ARMED, Pin.OUT)
led_tripped = Pin(cfg.PIN_LED_TRIPPED, Pin.OUT)
led_learn = Pin(cfg.PIN_LED_LEARN, Pin.OUT)

# --- State ---
STATE_ARMED = "armed"
STATE_LEARN = "learn"
STATE_TRIPPED = "tripped"

state = STATE_ARMED
baseline_amps = cfg.DEFAULT_BASELINE_AMPS
learned_amps = None
over_since_ms = None
last_irms = 0.0

# Button edge tracking
_prev = {"learn": 1, "save": 1, "reset": 1}


def trip_threshold():
    return baseline_amps * cfg.TRIP_RATIO


def set_trip(active):
    """Drive DLI switch port. active=True means cut PDU power."""
    if cfg.TRIP_ACTIVE_LOW:
        trip.value(0 if active else 1)
    else:
        trip.value(1 if active else 0)


def set_leds():
    led_armed.value(1 if state == STATE_ARMED else 0)
    led_tripped.value(1 if state == STATE_TRIPPED else 0)
    led_learn.value(1 if state == STATE_LEARN else 0)


def load_baseline():
    global baseline_amps
    try:
        with open(cfg.BASELINE_PATH, "r") as f:
            data = json.load(f)
        baseline_amps = float(data.get("baseline_amps", cfg.DEFAULT_BASELINE_AMPS))
        print("Loaded baseline: %.3f A (trip %.3f A)" % (baseline_amps, trip_threshold()))
    except OSError:
        baseline_amps = cfg.DEFAULT_BASELINE_AMPS
        print("Using factory baseline: %.3f A (trip %.3f A)" % (baseline_amps, trip_threshold()))


def save_baseline(amps):
    global baseline_amps
    baseline_amps = amps
    with open(cfg.BASELINE_PATH, "w") as f:
        json.dump({"baseline_amps": baseline_amps, "trip_ratio": cfg.TRIP_RATIO}, f)
    print("Saved baseline: %.3f A (trip %.3f A)" % (baseline_amps, trip_threshold()))


def read_adc_volt():
    # 16-bit read on Pico MicroPython; scale to volts
    raw = adc.read_u16()
    return (raw / 65535.0) * cfg.ADC_VREF


def measure_rms_amps():
    """Sample window, remove DC bias, return RMS amps."""
    n = cfg.RMS_WINDOW_SAMPLES
    period_us = int(1_000_000 / cfg.SAMPLE_HZ)
    samples = []
    for _ in range(n):
        samples.append(read_adc_volt())
        time.sleep_us(period_us)
    mean = sum(samples) / n
    acc = 0.0
    for v in samples:
        d = v - mean
        acc += d * d
    v_rms = math.sqrt(acc / n)
    return v_rms * cfg.AMPS_PER_ADC_VOLT


def pressed(name, pin):
    """Return True on falling edge (button to GND)."""
    global _prev
    val = pin.value()
    was = _prev[name]
    _prev[name] = val
    return was == 1 and val == 0


def enter_armed():
    global state, over_since_ms
    state = STATE_ARMED
    over_since_ms = None
    set_trip(False)
    set_leds()
    print("ARMED — baseline %.3f A trip %.3f A" % (baseline_amps, trip_threshold()))


def enter_tripped():
    global state, over_since_ms
    state = STATE_TRIPPED
    over_since_ms = None
    set_trip(True)
    set_leds()
    print("TRIPPED at %.3f A (threshold %.3f A)" % (last_irms, trip_threshold()))


def enter_learn():
    global state, learned_amps
    state = STATE_LEARN
    learned_amps = None
    set_leds()
    print("LEARN — sampling %.1f s..." % cfg.LEARN_SECONDS)


def run_learn():
    global learned_amps
    enter_learn()
    t_end = time.ticks_add(time.ticks_ms(), int(cfg.LEARN_SECONDS * 1000))
    acc = 0.0
    count = 0
    while time.ticks_diff(t_end, time.ticks_ms()) > 0:
        acc += measure_rms_amps()
        count += 1
        set_leds()
        # Allow abort via Reset
        if pressed("reset", btn_reset):
            print("LEARN aborted")
            enter_armed()
            return
    if count == 0:
        print("LEARN failed: no samples")
        enter_armed()
        return
    learned_amps = acc / count
    print("LEARN complete: %.3f A (press SAVE to store)" % learned_amps)
    # Stay in learn indicator briefly, then armed with pending learned value
    state = STATE_ARMED
    set_leds()
    led_learn.value(1)  # pending save indication


def now_ms():
    return time.ticks_ms()


def main():
    global last_irms, over_since_ms, state

    load_baseline()
    enter_armed()
    print("PDU Emergency Cutoff System ready")

    while True:
        last_irms = measure_rms_amps()

        if pressed("learn", btn_learn) and state != STATE_TRIPPED:
            run_learn()
            continue

        if pressed("save", btn_save) and state != STATE_TRIPPED:
            if learned_amps is not None:
                save_baseline(learned_amps)
                led_learn.value(0)
            else:
                print("Nothing to save — press LEARN first")
            if state != STATE_TRIPPED:
                enter_armed()
            continue

        if pressed("reset", btn_reset):
            if state == STATE_TRIPPED:
                # Allow reset after cutoff (current should collapse)
                enter_armed()
            else:
                print("Reset ignored (not tripped)")
            continue

        if state == STATE_ARMED:
            if last_irms >= trip_threshold():
                if over_since_ms is None:
                    over_since_ms = now_ms()
                elif time.ticks_diff(now_ms(), over_since_ms) >= cfg.TRIP_DEBOUNCE_MS:
                    enter_tripped()
            else:
                over_since_ms = None

        # Heartbeat print ~1 Hz
        # (avoid flooding; simple throttle)
        # MicroPython: use ticks
        set_leds()
        if state == STATE_ARMED and learned_amps is not None:
            led_learn.value(1)


if __name__ == "__main__":
    main()
