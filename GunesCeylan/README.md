# GunesCeylan

**Owner:** Güneş Ceylan
**Subsystem:** Power Management (lead). Also: Motion Control member, budget and procurement manager, UWB range pre-filtering (before localization).
**Related requirements** (Proposal Report, Table 2 and Table 3):
- Power: **C10** (≥ 30 min on one charge; M3: ≥ 15 min), **FR2.5** (stop ≤ 1 s, hardware e-stop), **FR5.2** (e-stop < 0.5 s; the GUI e-stop belongs to Furkan/Ömer, I support it with the hardware e-stop)
- Budget: **C6** (cost ≤ USD 350)
- UWB filtering: **FR1.1**, **FR1.2** (latency < 100 ms), **FR2.1**, **FR2.2**

## What this part does
- **Power Management:** Supplies every part of the robot from one 3S Li-ion pack (3 × Samsung 25R 18650 + BMS, 12.6 V full / 11.1 V nominal). Covers the 12 V motor rail (BTS7960 drivers), the 5 V rail for the Raspberry Pi, the ESP32 and sensors, fusing, the hardware e-stop, charging and battery-voltage monitoring.
- **Motion Control (member):** Helps with the drive system and low-level motor control. Şevval Nida Sağır leads it; see `SevvalNidaSagir/`.
- **Budget and procurement:** Tracks the team budget and what has been ordered, received and paid for.
- **UWB range filtering:** Cleans the raw UWB anchor ranges before they go to localization.

## Folder contents
| File | What |
|---|---|
| `generate_uwb_data.py` | Makes synthetic UWB ranges: 10 × 10 m arena, 4 corner anchors, 10 Hz, 120 s. Errors: noise σ = 5 cm, a constant offset for each anchor, 1 % spikes, NLOS on A2 (40–55 s), random dropouts and a dead A3 (80–90 s). `SEED = 42`. |
| `gating_filter.py` | Accepts or rejects each range using only past values, as it would on the robot. Range window 1.20–14.74 m. Max jump 1.5 m/s × dt + 0.30 m (0.45 m per sample at 10 Hz). Recovers after 3 rejections in a row that agree within 0.30 m. |

## How to run it
Needs Python 3 with `numpy` and `matplotlib`. Run from a working folder, because the scripts write their outputs to the current directory:
```
python3 generate_uwb_data.py   # writes uwb_synthetic.csv, arena_path.png, ranges_over_time.png
python3 gating_filter.py       # reads uwb_synthetic.csv; writes uwb_gated.csv, gating_result.png and prints a report
```
The power hardware is not built yet.

## Current status
- **UWB filtering (synthetic data):** The gating filter works. It catches 51/51 spikes and wrongly rejects 1 good value. Most of the remaining error comes from the constant offsets of each anchor (0.10–0.22 m), which gating cannot remove. RMS error after gating: A1 0.158 m, A2 0.300 m (offset plus NLOS), A3 0.110 m, A4 0.187 m. Next step is offset calibration.
- **Power, ordered on 16 Nov 2026 (planned parts, not final):**
  - 3 × Samsung 25R cells, 3S holder, 40 A 3S BMS
  - Inline blade fuse holder (ATO/ATC)
  - Red LED toggle switch (current rating to verify ≥ 10 A)
  - XL4015 5 A buck converter with voltmeter (set it to 5.1 V **before** connecting the Pi)
  - XT60 female and male with 12 AWG leads
- **Power, already bought:** 10 A standard blade fuses.
- **Power, still to buy:** 12.6 V ~2 A 3S charger and DC socket, 1000 µF ≥ 25 V capacitor, wire, heat-shrink, terminal block, e-stop.
- **Battery monitoring:** On the ESP32, through a 100k/22k divider, with a software cutoff around 9.9 V. The battery decision is logged in `SevvalNidaSagir/LOG.md`.
- **Pi:** The Proposal Report (Table 7) and Ömer's log both say Raspberry Pi 4, and the 5 V plan is sized for a Pi 4. Team to confirm.

## Open problems
- **Pi 4 vs Pi 5 (team to confirm):** Şevval's README says Pi 5. The XL4015 concern only matters if the team moves to a Pi 5 (5 V / 5 A).
- **Toggle switch:** Verify that its current rating is at least 10 A.
- **Budget (C6):**
  - Proposal Table 7 budgets 4 extra DWM3001CDK boards (USD 118), but Ömer's log says the course provides the anchors.
  - The USD 80 rent comes from Ömer's log and is not confirmed. Table 7 says rental costs are not confirmed yet.
- **Power budget (C10):** Not done yet. It needs the current draw of each load and the run time on 3 × 25R (2.5 Ah).
- **UWB:** The offsets cannot be calibrated until the real DWM3001CDK boards are measured.

## Large files (Google Drive links)
- None yet. The generated CSV/PNG outputs are small and can be regenerated with `SEED = 42`, so they are not committed.
