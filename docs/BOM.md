# Bill of Materials — PDU Emergency Cutoff System

| Qty | Item | Notes |
|-----|------|-------|
| 1 | APC UPS Pro 1500VA | Upstream UPS for rack |
| 1 | PDU (existing) | On 2-post open IT rack |
| 1 | DLI IoT Power Relay | Always On, Normally On, 2× Normally Off, switch port |
| 1 | SCT-013-005 | 5 A clamp-on CT |
| 1 | CT Bias Adapter | 3.3 V compatible preferred |
| 1 | Raspberry Pi Pico | RP2040; USB for flash/serial |
| 3 | Momentary pushbutton | Learn, Save, Reset |
| 3 | LED | Armed (G), Tripped (R), Learn (Y) |
| 3 | Resistor 330 Ω | LED current limit |
| 1 | Resistor 1 kΩ (optional) | Series on trip GPIO |
| 1 | 5 V USB PSU | From DLI Always On → Pico |
| — | Hookup wire, heat-shrink, cable ties | Low-voltage + CT lead management |
| — | Insulated pigtail / cord adapter (optional) | Accessible hot for CT clamp |

## Consumables / tools

- Multimeter (CAT III recommended for UPS outlet checks)
- Soldering iron or DuPont jumpers for breadboard prototype
- Micro-USB cable for Pico programming
