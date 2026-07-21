#!/usr/bin/env python3
"""Interactive simulator for the PDU Emergency Cutoff System.

Runs the real firmware (firmware/main.py, unmodified) in a background
thread against virtual hardware: CT + bias adapter (synthesized biased
60 Hz waveform into a fake ADC), DLI IoT Power Relay, pushbuttons, and
LEDs. You poll/drive the CT primary current from a small console.

Usage:
    python run_sim.py
"""

import threading

import bootstrap

bootstrap.setup()

import world              # noqa: E402  (needs bootstrap paths first)
import main as firmware   # noqa: E402
import config as cfg      # noqa: E402

HELP = """
Commands:
  i <amps>      set CT primary current, e.g.  i 0.55
  learn         press the Learn pushbutton
  save          press the Save pushbutton
  reset         press the Reset pushbutton
  status        show CT current, DLI relay, trip pin, LEDs
  leds          show all LED states
  led <name>    show one LED: armed, tripped, or learn
  help          show this help
  quit          exit the simulator
Factory trip: %.2f A x %.2f = %.3f A sustained %d ms
""" % (
    cfg.DEFAULT_BASELINE_AMPS,
    cfg.TRIP_RATIO,
    cfg.DEFAULT_BASELINE_AMPS * cfg.TRIP_RATIO,
    cfg.TRIP_DEBOUNCE_MS,
)


def print_status():
    s = world.WORLD.status()
    print("CT primary (set):       %.3f A" % s["ct_primary_set_amps"])
    print("CT primary (effective): %.3f A" % s["ct_primary_effective_amps"])
    print("DLI Normally On:        %s" % ("CLOSED (PDU on)" if s["dli_normally_on"] else "OPEN (PDU off)"))
    print("Trip pin (GP%d):        %s" % (cfg.PIN_TRIP, s["trip_pin_level"]))
    print_leds()


def print_leds(name=None):
    leds = world.WORLD.status()["leds"]
    if name is not None:
        key = name.upper()
        if key not in leds:
            print("Unknown LED: %s (use: armed, tripped, or learn)" % name)
            return
        print("%s LED: %s" % (key.title(), "ON" if leds[key] else "off"))
        return
    states = " ".join(
        "%s=%s" % (key, "ON" if level else "off")
        for key, level in leds.items()
    )
    print("LEDs:                   %s" % states)


def main():
    firmware_thread = threading.Thread(target=firmware.main, daemon=True)
    firmware_thread.start()

    print(HELP)
    while True:
        try:
            line = input("sim> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        parts = line.split()
        cmd = parts[0].lower()

        if cmd in ("i", "current") and len(parts) == 2:
            try:
                amps = float(parts[1])
            except ValueError:
                print("Not a number: %s" % parts[1])
                continue
            world.WORLD.set_current(amps)
            print("CT primary set to %.3f A" % amps)
        elif cmd in ("learn", "save", "reset"):
            world.WORLD.press_button(cmd)
            print("Pressed %s" % cmd.upper())
        elif cmd == "status":
            print_status()
        elif cmd == "leds":
            print_leds()
        elif cmd == "led" and len(parts) == 2:
            print_leds(parts[1])
        elif cmd == "help":
            print(HELP)
        elif cmd in ("quit", "exit", "q"):
            break
        else:
            print("Unknown command (try: help)")


if __name__ == "__main__":
    main()
