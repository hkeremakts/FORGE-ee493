# OmerFurkanDirier

**Owner:** Ömer Furkan Dirier
**Subsystem:** Communication (lead; member: Hüseyin Kerem Aktaş). Also responsible for the camera presentation.
**Related requirements:** FR5.1 (GUI ≥5 Hz, latency <0.5 s), FR5.2 (e-stop <0.5 s), FR2.3 (tolerate comm outage ≤2 s), FR2.5 (safe stop on comm loss >2 s)

## What this part does
Provides the data links between the Raspberry Pi 4 on RAPTOR and the ground-station PC: the camera stream to the PC (detection runs offboard on team PCs), detection results and commands back to the Pi, telemetry to the GUI, and the e-stop path.

## How to run it
Not runnable yet.

## Current status
Research and design phase. Nothing is built or measured yet.
- Pi 4 built-in Wi-Fi (CYW43455, 802.11ac, 1x1) is the candidate for the PC link; see LOG.md for sourced numbers.
- Stereo camera for the Pi 4 is undecided; see LOG.md.

## Open problems
- Real Wi-Fi throughput and ping across the arena are not measured (planned: iperf3).
- Whether to use our own router/access point, a PC hotspot, or campus Wi-Fi is undecided.
- End-to-end camera delay on Pi 4 + Camera V2 is unknown (no measurement found).
- Wi-Fi power save on the Pi must be checked and disabled (spikes up to 1.46 s reported elsewhere vs. the 0.5 s limit in FR5.2).
- IMX219-83 does not fit a single-CSI Pi 4 as-is; stereo options are unresolved.

## Large files (Google Drive links)
- None yet.
