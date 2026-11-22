# OmerFurkanDirier

**Owner:** Ömer Furkan Dirier
**Subsystem:** Communication (lead; member: Hüseyin Kerem Aktaş). Also responsible for the camera presentation.
**Related requirements:** FR5.1 (GUI ≥5 Hz, latency <0.5 s), FR5.2 (e-stop <0.5 s), FR2.3 (tolerate comm outage ≤2 s), FR2.5 (safe stop on comm loss >2 s)

## What this part does
Provides the data links between the Raspberry Pi 4 on RAPTOR and the ground-station PC: the camera stream to the PC (detection runs offboard on team PCs), detection results and commands back to the Pi, telemetry to the GUI, and the e-stop path.

## Folder contents
| Path | What |
|---|---|
| `PLAN.md` | Camera and communication plan (steps C1–C5, K1–K5) and reading list |
| `LOG.md` | Dated work log |
| `pi_esp32_link/` | Placeholder for the Pi–ESP32 serial protocol (not started) |

## How to run it
Not runnable yet.

## Current status
Research and planning phase. Nothing is built or measured yet.
- Working solution: single camera (Pi Camera V2, already owned) on the Pi 4. Stereo options were compared and set aside for now because of budget (about $270 left for everything) and one CSI port; see LOG.md 2026-11-22.
- Pi 4 built-in Wi-Fi is the candidate for the PC link; see LOG.md 2026-11-18 for sourced numbers.
- Detection model: Hüseyin Kerem Aktaş.

## Open problems
- Pi 4 vs Pi 5: Şevval's folder says Pi 5. Team must confirm.
- Pi operating system (Raspberry Pi OS vs Ubuntu) undecided.
- What the PC sends back to the robot (proposal: timestamped detections, not motor commands) not agreed.
- Single-camera ranging accuracy is only calculated, with assumed pixel errors. Needs measurement (PLAN.md step C3).
- Camera height and tilt undecided (mine to research); coordinate mast with Şevval.
- Real Wi-Fi throughput and ping across the arena not measured (iperf3). Router/access point choice open; may we bring our own?
- End-to-end camera delay on Pi 4 + Camera V2 unknown (PLAN.md step C5).
- Wi-Fi power save must be checked and disabled.
- Pi–ESP32 protocol not defined.

## Large files (Google Drive links)
- None yet.
