# Firmware (MicroPython) — Raspberry Pi Pico

## Features

- RMS current from SCT-013-005 via CT Bias Adapter on ADC0
- Trip when \(I_{rms} \ge I_{base} \times 1.30\) (debounce)
- Factory baseline **0.4 A** → trip **0.52 A**
- Learn / Save / Reset buttons
- Armed / Tripped / Learn LEDs
- Baseline persisted to `baseline.json` on flash

## Flash MicroPython

1. Download UF2 from https://micropython.org/download/RPI_PICO/
2. Hold BOOTSEL, plug USB, copy UF2 to the RPI-RP2 drive
3. Copy `config.py`, `main.py` to the Pico (Thonny, `mpremote`, or `scripts/flash.ps1`)

```powershell
mpremote connect COM3 cp firmware/config.py :config.py
mpremote connect COM3 cp firmware/main.py :main.py
mpremote connect COM3 reset
```

## Calibration

`AMPS_PER_ADC_VOLT` in `config.py` converts AC RMS volts at the ADC pin to amperes. Start with the SCT-013-005 + bias-adapter datasheet scale, then trim against a known load (kill-a-watt / clamp meter) at ~0.4 A.

## Files

| File | Role |
|------|------|
| `config.py` | Pins, thresholds, timing, scale |
| `main.py` | Sense loop, UI, trip latch, learn/save |
