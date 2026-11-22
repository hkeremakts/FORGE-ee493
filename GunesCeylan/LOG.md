# GunesCeylan – Work Log

Newest entry at the top. Format is defined in [RULEBOOK.md](../RULEBOOK.md).

### 2026-11-22 – README filled, power and budget status collected
- **What I did:** Read the RULEBOOK and my README/LOG. Filled README.md with my roles: Power Management lead, Motion Control member, budget and procurement manager, UWB range filtering. Collected power and budget facts that are already in teammates' folders (Şevval's drive-system log, Ömer's camera log) and listed the open power problems.
- **Decisions:**
  - **Decision:** For now, my README links to the battery decision in Şevval's LOG (3S Li-ion pack, 3 × Samsung 25R + BMS) and does not copy it as a new decision.
    **Alternatives considered:** Logging it again here as a new decision.
    **Reason:** The decision was made together on one date and is already logged there. Two copies could drift apart.
  - **Decision:** FR codes are left as "to be added". I did not guess them.
    **Alternatives considered:** Using placeholder FR numbers.
    **Reason:** The FR list is in the Proposal Report, which is not in the repository. Wrong codes would be misleading.
- **Results / measurements:** None. No hardware work this session.
- **Problems / open questions:**
  - Pi 4 or Pi 5? The teammates' folders disagree, and the 5 V rail sizing depends on it.
  - The XL4015 5 A converter is marginal for a Pi 5.
  - The charger and the fuses are not chosen.
  - Budget: about $270 of $350 left (from Ömer's log). This needs to be confirmed and tracked in one place.
- **Next steps:**
  1. Confirm Pi 4 vs Pi 5 with the team.
  2. Write a power budget: current for each load (Pi, motors at stall, ESP32, UWB, camera), peak and average draw, run time on 3 × 25R (2.5 Ah).
  3. Choose the 5 V converter, the fuses and the 3S charger.
  4. Start a budget and procurement tracker in this folder.
  5. Get FR codes from the Proposal Report and link them.

### 2026-11-14 – Folder created
- **What I did:** Folder, README.md and LOG.md created from the team template.
- **Decisions:** –
- **Results / measurements:** –
- **Problems / open questions:** –
- **Next steps:** Fill in README.md (subsystem, related FR codes) and start logging work.
