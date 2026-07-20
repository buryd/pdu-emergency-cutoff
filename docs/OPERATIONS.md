# Operations guide

## First power-on

1. Confirm wiring per `docs/WIRING.md`.
2. Power UPS → DLI → Pico (Always On) → PDU (Normally On).
3. Armed LED should light. Serial (optional) prints factory baseline **0.4 A**, trip **0.52 A**.

## Learn a new baseline

1. Run the rack at normal steady load.
2. Press **Learn** — Learn LED on for ~5 s.
3. Press **Save** — baseline written to flash; trip = baseline × 1.30.
4. Learn LED turns off when saved (or stays on if pending save).

## After a trip

1. Tripped LED on; PDU dark (Normally On open).
2. Investigate overload / fault.
3. Remove excess load if needed.
4. Press **Reset** — Armed LED on; PDU restores.

## Factory defaults

| Parameter | Value |
|-----------|-------|
| Baseline | 0.4 A |
| Trip ratio | +30% |
| Trip current | 0.52 A |

Delete `baseline.json` on the Pico (or re-flash) to restore factory baseline.

## Recommended DLI roles

| Outlet | Use |
|--------|-----|
| Always On | Pico 5 V supply |
| Normally On | PDU |
| Normally Off | Unused / staged gear |
| Switch port | Pico GP15 trip |
