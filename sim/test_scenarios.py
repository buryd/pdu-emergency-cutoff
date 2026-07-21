#!/usr/bin/env python3
"""Headless functional tests of the PDU Emergency Cutoff design.

Runs the unmodified firmware against the virtual hardware and checks:

1. Boots into Armed with the PDU energized
2. Normal 0.40 A baseline current does not trip
3. A brief blip above the trip level is ignored (debounce)
4. Sustained overcurrent trips the DLI, PDU goes dead, current collapses
5. Reset clears the latch and restores the PDU
6. Learn + Save stores a new baseline and shifts the trip point

Usage:
    python test_scenarios.py
"""

import os
import threading
import time

import bootstrap

bootstrap.setup()

# Fresh factory state: remove any previously saved baseline
if os.path.exists("baseline.json"):
    os.remove("baseline.json")

import world              # noqa: E402
import main as firmware   # noqa: E402
import config as cfg      # noqa: E402

W = world.WORLD
W.verbose = False

FAILURES = []


def wait_for(cond, timeout_s, what):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if cond():
            return
        time.sleep(0.05)
    raise AssertionError("timed out waiting for: " + what)


def hold(seconds):
    time.sleep(seconds)


def check(name, fn):
    try:
        fn()
        print("PASS  %s" % name)
    except AssertionError as exc:
        FAILURES.append((name, str(exc)))
        print("FAIL  %s: %s" % (name, exc))


def leds():
    return W.status()["leds"]


def t1_boots_armed():
    wait_for(lambda: W.relay_on and W.trip_pin_level is not None, 3, "armed boot")
    assert leds()["ARMED"] == 1, "Armed LED should be on"
    assert leds()["TRIPPED"] == 0, "Tripped LED should be off"


def t2_baseline_no_trip():
    W.set_current(0.40)
    hold(1.5)
    assert W.relay_on, "relay must stay closed at 0.40 A baseline"


def t3_brief_blip_ignored():
    W.set_current(0.55)
    hold(0.12)
    W.set_current(0.40)
    hold(1.0)
    assert W.relay_on, "a %d ms blip must not trip (debounce %d ms)" % (
        120, cfg.TRIP_DEBOUNCE_MS)


def t4_sustained_overcurrent_trips():
    W.set_current(0.60)
    wait_for(lambda: not W.relay_on, 3, "trip at 0.60 A sustained")
    assert leds()["TRIPPED"] == 1, "Tripped LED should be on"
    assert leds()["ARMED"] == 0, "Armed LED should be off"
    assert W.effective_amps() == 0.0, "PDU dead -> CT current collapses"


def t5_reset_restores():
    W.set_current(0.40)
    W.press_button("reset")
    wait_for(lambda: W.relay_on, 3, "reset re-arms and restores PDU")
    assert leds()["ARMED"] == 1, "Armed LED should be back on"
    assert leds()["TRIPPED"] == 0, "Tripped LED should be off"


def t6_learn_save_new_baseline():
    W.set_current(0.45)          # below factory 0.52 A trip, safe to learn
    hold(0.5)
    W.press_button("learn")
    hold(cfg.LEARN_SECONDS + 2)  # learn window
    W.press_button("save")
    wait_for(lambda: os.path.exists("baseline.json"), 3, "baseline.json saved")

    import json
    with open("baseline.json") as f:
        saved = json.load(f)["baseline_amps"]
    assert abs(saved - 0.45) < 0.05, "saved baseline %.3f not near 0.45 A" % saved

    # 0.55 A > old 0.52 A trip but < new 0.585 A trip: must stay armed
    W.set_current(0.55)
    hold(1.5)
    assert W.relay_on, "0.55 A must not trip after learning 0.45 A baseline"

    # Well above the new threshold: must trip
    W.set_current(0.85)
    wait_for(lambda: not W.relay_on, 3, "trip above learned threshold")


def main():
    threading.Thread(target=firmware.main, daemon=True).start()

    check("1. boots into Armed, PDU energized", t1_boots_armed)
    check("2. 0.40 A baseline does not trip", t2_baseline_no_trip)
    check("3. brief blip ignored by debounce", t3_brief_blip_ignored)
    check("4. sustained 0.60 A trips DLI, PDU dead", t4_sustained_overcurrent_trips)
    check("5. Reset clears latch, PDU restored", t5_reset_restores)
    check("6. Learn/Save moves baseline and trip point", t6_learn_save_new_baseline)

    print()
    if FAILURES:
        print("%d test(s) FAILED" % len(FAILURES))
        raise SystemExit(1)
    print("All 6 scenarios passed.")


if __name__ == "__main__":
    main()
