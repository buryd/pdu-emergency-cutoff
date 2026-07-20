# Architecture — PDU Emergency Cutoff System

## Purpose

Protect a 2-post open IT rack by cutting AC to the PDU when input current exceeds **130% of baseline** (normal operating current). Startup baseline is **0.4 A**; trip point is **0.52 A** until a new baseline is learned and saved.

## Block diagram

```
                    ┌─────────────────────┐
   AC utility ─────►│  APC UPS Pro 1500VA │
                    └──────────┬──────────┘
                               │ UPS output (line / neutral / ground)
                               ▼
                    ┌─────────────────────┐
                    │  DLI IoT Power Relay│
                    │  ┌───────────────┐  │
                    │  │ Always On     │──┼── optional: Pico USB PSU / DLI itself
                    │  │ Normally On   │──┼──► PDU input ──► rack loads
                    │  │ Normally Off×2│  │   (unused or spare)
                    │  │ Switch port   │◄─┼── Pico GPIO (trip / enable)
                    │  └───────────────┘  │
                    └─────────────────────┘
                               │
                    SCT-013-005 clamped on
                    PDU hot conductor
                               │
                               ▼
                    ┌─────────────────────┐
                    │   CT Bias Adapter   │──── mid-biased AC voltage
                    └──────────┬──────────┘
                               │ ADC in
                               ▼
                    ┌─────────────────────┐
                    │ Raspberry Pi Pico   │
                    │  · RMS current calc │
                    │  · 30% trip logic   │
                    │  · Learn/Save/Reset │
                    │  · LED status       │
                    └──────────┬──────────┘
                               │
              Learn / Save / Reset PBs
              Armed / Tripped / Learn LEDs
```

## Why each device

| Device | Why it is in the design |
|--------|-------------------------|
| **APC UPS Pro 1500VA** | Provides backup and surge-protected AC for the rack chain; sits upstream of the cutoff relay so UPS batteries still feed the DLI/PDU path until trip. |
| **SCT-013-005** | 5 A full-scale clamp CT; well matched to a ~0.4 A baseline (good ADC headroom without saturation at modest overloads). Non-invasive — no series shunt in the mains path. |
| **CT Bias Adapter** | Pico ADC is 0–3.3 V single-ended; CT AC output must be biased to ~Vref/2 so positive and negative half-cycles can be sampled for RMS. |
| **DLI IoT Power Relay** | Hard AC cutoff with labeled receptacle modes. **Normally On** feeds the PDU (energized until switch/network deasserts). **Switch port** gives local dry-contact / logic control from the Pico without depending on LAN. Always On can power the Pico PSU so the controller stays alive after trip. |
| **Raspberry Pi Pico** | Fast ADC sampling, deterministic GPIO for trip, tiny flash for baseline storage, no OS latency. |
| **Learn / Save / Reset** | Field calibration and latch clear without a laptop. |
| **Armed / Tripped / Learn LEDs** | Immediate rack-side state visibility. |

## Operating modes

### 1. Armed (normal)

- DLI Normally On receptacle **energized** → PDU powered.
- Pico samples CT, computes RMS, compares to \(I_{base} \times 1.30\).
- Armed LED **ON**; Tripped/Learn **OFF**.

### 2. Learn

- Operator presses **Learn** while the rack is at normal steady load.
- Pico averages RMS for a configurable window (default 5 s).
- Learn LED **ON** during acquisition.
- Result held in RAM until **Save** (or discarded on timeout/Reset).

### 3. Save

- Persists learned \(I_{base}\) to Pico flash (`baseline.json`).
- Recomputes trip threshold = \(I_{base} \times 1.30\).
- Returns to Armed.

### 4. Tripped

- Condition: \(I_{rms} \ge I_{trip}\) for **N** consecutive samples (debounce, default ~200 ms equivalent).
- Pico asserts trip on DLI switch port → Normally On **opens** → PDU dead.
- Tripped LED **ON**; Armed **OFF**.
- Latch held until **Reset**.

### 5. Reset

- Clears trip latch only if measured current is below trip (or CT shows near-zero after cutoff — see firmware note).
- Re-energizes DLI path and returns to Armed.
- Does **not** erase saved baseline unless Learn/Save sequence is used again.

## Signal chain (current sense)

1. SCT-013-005 secondary → CT Bias Adapter.
2. Bias adapter → Pico **ADC0 (GP26)**.
3. Sample at ≥ 2 kHz for several 60 Hz cycles; compute true RMS of AC component (remove DC bias).
4. Scale ADC → amperes using calibration constants for SCT-013-005 + burden/bias network (see `firmware/config.py`).

### Default thresholds

| Parameter | Value |
|-----------|-------|
| Factory baseline \(I_{base}\) | 0.40 A |
| Trip ratio | 1.30 (30% above baseline) |
| Factory trip \(I_{trip}\) | 0.52 A |
| Debounce | ~200 ms sustained overcurrent |
| CT full scale | 5 A |

## DLI receptacle assignment (recommended)

| Receptacle | Connection |
|------------|------------|
| **Always On** | 5 V USB wall wart / PSU for Raspberry Pi Pico (survives PDU trip) |
| **Normally On** | PDU AC input cord |
| **Normally Off #1 / #2** | Spare / future staged loads |
| **Switch port** | Pico trip GPIO + GND (active level per DLI docs — firmware uses active-low open-drain style by default) |

## Safety model

- Fail-safe preference: on Pico brownout, DLI switch state should leave PDU **off** or known-safe; verify DLI switch-port default with your unit’s manual and set `TRIP_ACTIVE_LOW` accordingly.
- Mains wiring only by a qualified person; CT on insulated conductor; earth continuity preserved through DLI/PDU.
- This is an **emergency cutoff**, not a code-listed circuit breaker replacement.

## Failure modes (summary)

| Failure | Expected behavior |
|---------|-------------------|
| Overcurrent | Trip, latch, Tripped LED |
| CT open / bias fault | Firmware treats as invalid → optional safe trip (configurable) |
| Pico power loss | Pico PSU on Always On; if both lose power, DLI follows its unpowered switch default |
| False trip | Re-Learn under true normal load; increase debounce if needed |
