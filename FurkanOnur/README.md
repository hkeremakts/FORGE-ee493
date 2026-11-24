# FurkanOnur

**Owner:** Furkan Onur
**Subsystem:** User Interface and Ground Station (lead). Also: Power Management member, Motion Control member.
**Related requirements** (Proposal Report, Table 2 and Table 3; taken from teammates' READMEs, still to be checked against the report):
- UI / Ground Station: **FR5.1** (GUI update ≥ 5 Hz, latency < 0.5 s), **FR5.2** (GUI e-stop < 0.5 s; shared with Ömer Furkan Dirier, Güneş Ceylan provides the hardware e-stop)
- Communication-related, affects the GUI: **FR2.3** (tolerate comm outage ≤ 2 s), **FR2.5** (safe stop on comm loss > 2 s)
- Power Management: **C10** (≥ 30 min on one charge; M3 ≥ 15 min)

## What this part does
The ground-station GUI on the team PC: shows RAPTOR's telemetry (pose, state, battery), the camera stream and detection results, lets the operator send waypoints and commands, and provides the software e-stop. Data links themselves are built by the Communication subsystem (Ömer Furkan Dirier).

## How to run it
Not runnable yet.

## Current status
- Folder set up, subsystem and requirements filled in.
- No GUI code yet.

## Open problems
- GUI framework not chosen yet.
- Telemetry/command message format must be agreed with Communication (Ömer) — likely in `/shared/`.
- FR codes above need checking against the Proposal Report.

## Large files (Google Drive links)
- _None yet. Datasets, videos, model weights: link them here, never commit them._
