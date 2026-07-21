# Simulator — virtual bench for the PDU Emergency Cutoff System

Runs the **real, unmodified firmware** (`firmware/main.py` + `firmware/config.py`)
on a PC against virtual hardware. Nothing in `firmware/`, `docs/`, or
`hardware/` is changed — the design stays frozen.

## What is virtualized

| Real device | Simulation |
|-------------|------------|
| CT primary current | A settable amps value you poll/drive from the console |
| SCT-013-005 + CT Bias Adapter | 60 Hz sine riding on the 1.65 V mid-rail, scaled with the firmware's own `AMPS_PER_ADC_VOLT` |
| Pico ADC (GP26) | Mock `machine.ADC` returning that waveform as 16-bit counts |
| DLI IoT Power Relay | Watches the trip GPIO; Normally On opens on trip, which also collapses measured current to 0 A |
| Learn / Save / Reset buttons | `learn` / `save` / `reset` commands hold the pin low briefly |
| Armed / Tripped / Learn LEDs | Levels recorded from firmware writes, shown by `status` |

How it works: `sim/machine.py` shadows MicroPython's `machine` module, and
`bootstrap.py` adds the MicroPython `time` functions (`ticks_ms`, `sleep_us`, ...)
to CPython. The firmware imports resolve to these mocks; its logic runs as-is.

## Requirements

Python 3.8+ (3.11+ recommended for accurate sample timing). No packages needed.

## Interactive bench

```powershell
cd sim
python run_sim.py
```

```
sim> status          # CT amps, DLI relay, trip pin, LEDs
sim> i 0.55          # raise CT primary above the 0.52 A factory trip
[DLI] Trip asserted -> Normally On OPEN, PDU is OFF
sim> reset           # clear the latch after lowering current
sim> learn           # then wait ~5 s
sim> save            # persist new baseline (sim/.state/baseline.json)
sim> quit
```

## Automated functional tests

```powershell
cd sim
python test_scenarios.py
```

Verifies: boots Armed → 0.40 A holds → brief blip ignored (200 ms debounce) →
sustained 0.60 A trips and kills the PDU → Reset restores → Learn/Save moves
the baseline and trip point.

## State

The saved baseline goes to `sim/.state/baseline.json` (ignored by git),
mirroring the Pico's flash file. Delete it to return to the factory 0.4 A.
