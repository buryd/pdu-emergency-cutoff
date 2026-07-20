# Wiring — PDU Emergency Cutoff System

See [SAFETY.md](SAFETY.md) before any mains work.

## 1. AC power path (mains)

```
APC UPS Pro 1500VA OUTPUT
        │
        ▼
DLI IoT Power Relay INPUT (line, neutral, ground)
        │
        ├── Always On receptacle ──► 5 V USB PSU ──► Pico USB (or VSYS)
        │
        └── Normally On receptacle ──► PDU power inlet
                                            │
                                            ▼
                                     2-post rack loads
```

1. Plug DLI into UPS output (or hardwire if your DLI model supports it — follow DLI manual).
2. Plug PDU into DLI **Normally On**.
3. Power Pico from DLI **Always On** so the controller remains powered after a PDU trip.

## 2. Current transformer

1. Separate the PDU cord’s hot conductor (or use a short pigtail with accessible hot).
2. Clamp **SCT-013-005** around the hot only.
3. Plug CT into **CT Bias Adapter** input.
4. Bias adapter output → Pico:

| Bias adapter | Pico |
|--------------|------|
| Signal / OUT | GP26 (ADC0) |
| VCC / 3V3 | 3V3 |
| GND | GND |

Exact silkscreen names vary by bias-adapter vendor; match signal, 3.3 V, and ground.

## 3. DLI switch port → Pico

Consult your DLI switch-port pinout (typically a 3.5 mm or terminal pair for external control).

| DLI switch port | Pico |
|-----------------|------|
| Control / SIG | GP15 (trip output) |
| GND | GND |

Default firmware: **active-low** trip (`TRIP_ACTIVE_LOW = True`) — GPIO drives low to command cutoff. Invert in `firmware/config.py` if your DLI expects active-high.

Optional: series 1 kΩ resistor from GP15 to SIG for protection.

## 4. Front-panel UI (3.3 V logic)

### Pushbuttons (to GND, internal pull-ups)

| Switch | Pico GPIO |
|--------|-----------|
| Learn | GP10 |
| Save | GP11 |
| Reset | GP12 |

### LEDs (GPIO → resistor → LED → GND)

| LED | Pico GPIO | Suggested series R |
|-----|-----------|--------------------|
| Armed (green) | GP16 | 330 Ω |
| Tripped (red) | GP17 | 330 Ω |
| Learn (yellow/amber) | GP18 | 330 Ω |

## 5. Mechanical (2-post rack)

- Mount DLI and UPS per manufacturer rack/floor guidance.
- Secure Pico on a DIN/rail or insulated plate on the rack rail (not across bus bars).
- Strain-relieve the CT lead; keep low-voltage wiring bundled away from mains.

## 6. Commissioning checklist

- [ ] Earth continuity verified UPS → DLI → PDU
- [ ] CT on hot only; bias adapter powered from Pico 3V3
- [ ] Pico powered from Always On
- [ ] PDU on Normally On
- [ ] Switch-port polarity confirmed with a lamp/load test
- [ ] Learn → Save at 0.4 A (or measured normal load)
- [ ] Verify trip ≈ 130% of baseline with a controlled load bank if available
- [ ] Reset restores Armed and PDU power
