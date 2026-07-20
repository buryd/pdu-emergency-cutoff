# Safety

**Mains voltage can kill.** Treat every conductor downstream of the UPS as live until proven otherwise.

## Before you start

- Work only if you are qualified for AC wiring in your jurisdiction.
- De-energize and lock out the UPS output before opening the DLI or PDU cord path.
- Use a properly rated CAT meter to verify zero voltage.
- Keep protective earth continuous from UPS → DLI → PDU → equipment.
- Mount the Pico and low-voltage UI away from exposed mains terminals.

## CT installation

- Clamp the SCT-013-005 around **one** current-carrying conductor (hot), never hot+neutral together.
- Prefer clamping an insulated cord section; do not cut insulation.
- Orient the clamp per manufacturer marking; direction affects phase only (RMS magnitude is used).

## DLI IoT Power Relay

- Confirm receptacle ratings vs UPS and PDU load.
- Understand **Always On / Normally On / Normally Off** behavior for *your* firmware/network config and switch-port polarity.
- Test trip/reset with a dummy load before connecting production servers.

## Not a substitute for

- Branch-circuit breakers or fuses
- Listed EPO systems required by code/fire marshal
- Arc-flash PPE and rack grounding practices

## Liability

This project is provided as a design reference. Validate thresholds, wiring, and fail-safe defaults in your environment before relying on it to protect equipment.
