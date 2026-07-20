# Pin map — Raspberry Pi Pico

| Function | GPIO | Pico pin | Direction | Notes |
|----------|------|----------|-----------|-------|
| CT sense (ADC) | GP26 | 31 | Analog in | ADC0 ← CT Bias Adapter OUT |
| Learn PB | GP10 | 14 | Input pull-up | Active low to GND |
| Save PB | GP11 | 15 | Input pull-up | Active low to GND |
| Reset PB | GP12 | 16 | Input pull-up | Active low to GND |
| Trip → DLI switch | GP15 | 20 | Output | Default active-low |
| Armed LED | GP16 | 21 | Output | High = on |
| Tripped LED | GP17 | 22 | Output | High = on |
| Learn LED | GP18 | 24 | Output | High = on |
| 3V3 | 3V3 | 36 | Power | Bias adapter VCC |
| GND | GND | 38 / 3 / 18 | Ground | Common with DLI switch GND |

```
CT Bias Adapter OUT ──► GP26
Learn PB ── GND        GP10
Save PB ── GND         GP11
Reset PB ── GND        GP12
DLI switch SIG ◄──     GP15
Armed LED ◄──          GP16
Tripped LED ◄──        GP17
Learn LED ◄──          GP18
```
