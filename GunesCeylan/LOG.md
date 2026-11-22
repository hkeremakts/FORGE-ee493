# GunesCeylan – Work Log

Newest entry at the top. Format is defined in [RULEBOOK.md](../RULEBOOK.md).

### 2026-11-22 – README filled, UWB gating filter, power parts status
- **What I did:**
  - Filled README.md with my roles (Power Management lead, Motion Control member, budget and procurement manager, UWB range filtering) and the related requirements.
  - Uploaded `generate_uwb_data.py`, which makes synthetic UWB ranges: 10 × 10 m arena, noise σ = 5 cm, an offset for each anchor, 1 % spikes, NLOS on A2, dropouts, `SEED = 42`.
  - Uploaded `gating_filter.py`, which rejects bad ranges: range window 1.20–14.74 m, max jump 0.45 m per sample, recovery after 3 rejections in a row that agree with each other. FR1.1, FR1.2, FR2.1, FR2.2.
  - Recorded the power parts ordered on 16 Nov 2026 (planned, not final), the parts already bought and the parts still to buy (see README).
- **Decisions:**
  - **Decision:** My README links to the battery decision in Şevval's LOG (3S Li-ion pack, 3 × Samsung 25R + BMS). I do not log it again here.
    **Alternatives considered:** Logging it again here as a new decision.
    **Reason:** We made the decision together, and it is already logged there. Two copies could drift apart.
  - **Decision:** Related requirements, from Proposal Report Table 2 and Table 3:
    - Power: C10 (≥ 30 min on one charge; M3 ≥ 15 min), FR2.5 (stop ≤ 1 s, hardware e-stop), FR5.2 (e-stop < 0.5 s; I support the GUI e-stop of Furkan/Ömer with the hardware e-stop)
    - Budget: C6 (cost ≤ USD 350)
    - UWB filtering: FR1.1, FR1.2 (latency < 100 ms), FR2.1, FR2.2

    **Alternatives considered:** Leaving the codes as "to be added" until the Proposal Report is in the repository.
    **Reason:** The codes are now taken directly from Table 2 and Table 3, so every task and test can be linked to one.
  - **Decision:** Remove spikes by gating with simple physical rules (range window 1.20–14.74 m, max jump 1.5 m/s × dt + 0.30 m from the last accepted value, accept a new level after 3 consistent rejections within 0.30 m). Rejected values are marked invalid, not replaced.
    **Alternatives considered:** Smoothing the spikes away with a moving average or a median filter.
    **Reason:** A moving average is pulled off by every spike. A median filter removes spikes but adds delay, and the latency budget is < 100 ms (FR1.2). Physical-rule gating adds no delay, and marking values invalid tells localization that the anchor is missing. Recovery stops the filter from getting stuck after a real sudden change.
- **Results / measurements:**
  - Gating filter on the synthetic data (re-run and reproduced today):
    - 51/51 spikes caught; 1 good value wrongly rejected (on A2).
    - 58 jump rejections and 0 out-of-range rejections in total.
  - RMS error, before → after gating:

    | Anchor | Before | After |
    |---|---|---|
    | A1 | 0.261 m | 0.158 m |
    | A2 | 0.339 m | 0.300 m |
    | A3 | 0.226 m | 0.110 m |
    | A4 | 0.296 m | 0.187 m |

  - Most of the remaining error is the constant offset of each anchor (0.10–0.22 m). On A2 it also includes the NLOS bias. Gating cannot remove either.
- **Problems / open questions:**
  - Pi 4 or Pi 5? Proposal Table 7 and Ömer's log say Pi 4, and my 5 V plan is for a Pi 4. Şevval's README says Pi 5. The XL4015 5 A concern only applies to a Pi 5. Team to confirm.
  - The toggle switch's current rating must be verified (≥ 10 A).
  - Budget (C6):
    - Proposal Table 7 budgets 4 extra DWM3001CDK (USD 118), but Ömer's log says the course provides the anchors.
    - The USD 80 rent is from Ömer's log and is not confirmed. Table 7 says rental costs are not confirmed yet.
  - With these rules the range window never triggered. All bad values were caught by the jump rule.
- **Next steps:**
  1. UWB: calibrate the offset of each anchor (first on synthetic data, then on the real DWM3001CDK). FR1.1, FR1.2.
  2. Confirm Pi 4 vs Pi 5 with the team.
  3. Write the power budget: current for each load, peak and average draw, run time on 3 × 25R (2.5 Ah), checked against C10 (≥ 30 min; M3 ≥ 15 min).
  4. Buy the remaining parts: charger and DC socket, 1000 µF capacitor, wire, heat-shrink, terminal block, e-stop. Plan the hardware e-stop for FR2.5 and FR5.2.
  5. Start a budget and procurement tracker in this folder (C6) and settle the DWM3001CDK and rent questions.

### 2026-11-14 – Folder created
- **What I did:** Folder, README.md and LOG.md created from the team template.
- **Decisions:** –
- **Results / measurements:** –
- **Problems / open questions:** –
- **Next steps:** Fill in README.md (subsystem, related FR codes) and start logging work.
