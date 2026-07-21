"""Host-PC bootstrap for simulating the unmodified Pico firmware.

Puts firmware/ (real config.py, main.py) and sim/ (mock machine module)
on sys.path, moves the working directory to sim/.state so baseline.json
is written there, and adds the MicroPython time functions that
firmware/main.py expects (ticks_ms, ticks_add, ticks_diff, sleep_us)
to CPython's time module.
"""

import os
import sys
import time as _time

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SIM_DIR)
FIRMWARE_DIR = os.path.join(REPO_ROOT, "firmware")
STATE_DIR = os.path.join(SIM_DIR, ".state")


def _sleep_us(us):
    # time.sleep() granularity on some platforms is too coarse for the
    # firmware's 500 us sample spacing, so short waits are busy-waited.
    if us >= 2000:
        _time.sleep(us / 1_000_000)
        return
    end = _time.perf_counter() + us / 1_000_000
    while _time.perf_counter() < end:
        pass


def setup():
    os.makedirs(STATE_DIR, exist_ok=True)
    os.chdir(STATE_DIR)

    for path in (FIRMWARE_DIR, SIM_DIR):
        if path not in sys.path:
            sys.path.insert(0, path)

    if not hasattr(_time, "ticks_ms"):
        # perf_counter: monotonic() may only have ~15.6 ms resolution on Windows
        _time.ticks_ms = lambda: int(_time.perf_counter() * 1000)
        _time.ticks_add = lambda t, delta: t + delta
        _time.ticks_diff = lambda a, b: a - b
        _time.sleep_us = _sleep_us
