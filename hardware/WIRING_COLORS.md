# Wire colors — device layout

Authoritative color coding for connections between devices. Use with `device-layout.png`.

| Color | Meaning | Connections |
|-------|---------|-------------|
| **Blue** | AC mains | UPS → DLI → PDU → rack loads; DLI Always On → 5 V USB PSU |
| **Orange** | CT analog sense | SCT-013-005 → CT Bias Adapter **IN**; Adapter **OUT** → Pico **GP26** only |
| **Purple** | Low-voltage logic | Pico **3V3** → Adapter **VCC**; 5 V USB → Pico USB; buttons → GP10–12; LEDs → GP16–18 |
| **Black** | Ground only | Common GND: Pico, adapter, buttons, LEDs, DLI switch GND |
| **Green (dashed)** | Trip control | Pico **GP15** → DLI switch port |

## CT Bias Adapter (do not mix colors on one pin)

| Terminal | Color | From / to |
|----------|-------|-----------|
| VCC | Purple | Pico 3V3 |
| IN | Orange | SCT-013-005 jack |
| GND | Black | Common GND |
| OUT | Orange | Pico GP26 (ADC0) |

**Never** tie VCC, IN, and GND together.

## What orange is not

- Not USB
- Not 3V3
- Not GND
- Not trip GPIO
