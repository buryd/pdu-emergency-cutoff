"""Mock of MicroPython's `machine` module for host-PC simulation.

firmware/main.py does `from machine import ADC, Pin`; with sim/ on
sys.path it gets these classes, which delegate to the virtual world
instead of RP2040 hardware. The firmware itself is untouched.
"""

import world


class Pin:
    IN = 0
    OUT = 1
    PULL_UP = 2
    PULL_DOWN = 3

    def __init__(self, gpio, mode=-1, pull=None):
        self.gpio = gpio
        self.mode = mode
        self.pull = pull

    def value(self, v=None):
        if v is None:
            return world.WORLD.read_pin(self.gpio)
        world.WORLD.write_pin(self.gpio, 1 if v else 0)


class ADC:
    def __init__(self, gpio):
        self.gpio = gpio

    def read_u16(self):
        return world.WORLD.adc_read_u16()
