# BOM — DIY CT Bias Adapter

For **SCT-013-005** → Raspberry Pi Pico (3.3 V). Voltage-output CT: **no external burden**.

See schematic: [ctbiasadapter-layout.png](ctbiasadapter-layout.png)

| Qty | Item | Spec / notes |
|-----|------|----------------|
| 2 | Resistor | 10 kΩ, 1% preferred (matched pair for ~1.65 V mid-bias) |
| 1 | Capacitor | 10 µF; electrolytic OK (+ to mid-point, − to GND) or ceramic ≥10 µF |
| 1 | 3.5 mm stereo jack | Female, panel or PCB; mates with SCT-013 plug |
| 1 | Protoboard / PCB | Small perfboard or solderable breadboard |
| — | Hookup wire | 3 leads: 3V3, GND, OUT → Pico |
| 1 | Resistor 1 kΩ (optional) | Series between OUT and GP26 for ADC protection |

## Pico connections (not extra BOM items)

| Adapter | Pico |
|---------|------|
| 3V3 / VCC | 3V3 |
| GND | GND |
| OUT | GP26 (ADC0) |

## Notes

- Power the divider from Pico **3.3 V only** (not 5 V).
- Idle OUT should measure ≈ **1.65 V DC** before calibration.
- CT clamp and Pico are listed on the main system BOM: [docs/BOM.md](../docs/BOM.md).
