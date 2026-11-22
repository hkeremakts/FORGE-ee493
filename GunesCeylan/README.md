# GunesCeylan

**Owner:** Güneş Ceylan
**Subsystem:** Power Management (lead). Also: Motion Control member, budget and procurement manager, UWB range pre-filtering (before localization).
**Related requirements:** _FR codes to be added from the Proposal Report (Requirement Analysis)_

## What this part does
- **Power Management:** Supplies every part of the robot from one 3S Li-ion pack (3 × Samsung 25R 18650 + BMS, 12.6 V full / 11.1 V nominal). Covers the 12 V motor rail (BTS7960 drivers), the 5 V rail for the Raspberry Pi, the ESP32 and sensors, fusing, charging and battery-voltage monitoring.
- **Motion Control (member):** Helps with the drive system and low-level motor control. Şevval Nida Sağır leads it; see `SevvalNidaSagir/`.
- **Budget and procurement:** Tracks the team budget and what has been ordered, received and paid for.
- **UWB range filtering:** Cleans the raw UWB anchor ranges (outlier rejection, smoothing) before they go to localization.

## How to run it
Not runnable yet.

## Current status
- **Power:**
  - Battery decided: keep the team's existing 3S Li-ion pack (decision logged with Şevval, `SevvalNidaSagir/LOG.md`, 2026-11).
  - Battery voltage is read on the ESP32 through a 100k/22k divider, with a software cutoff around 9.9 V.
  - Not yet chosen: the 5 V converter for the Pi, fuses, the 3S charger.
- **Budget:** Total $350, about $80 of it already spent on equipment rent, so about $270 is left (figures from `OmerFurkanDirier/LOG.md`). No budget tracker in this folder yet.
- **UWB filtering:** Not started. The department supplied one DWM3001CDK, and the course provides the four anchors.

## Open problems
- The XL4015 5 A buck converter is marginal for a Raspberry Pi 5 (needs 5 V / 5 A). Choose a converter with real margin.
- Pi 4 or Pi 5? Şevval's README says Pi 5 and Ömer's log says the department supplied a Pi 4. The 5 V rail depends on the answer.
- The 3S charger and the fuses (battery main fuse, motor rail) are not bought.
- No power budget yet (current draw for each load, expected run time).
- FR codes are not linked yet.

## Large files (Google Drive links)
- None yet.
