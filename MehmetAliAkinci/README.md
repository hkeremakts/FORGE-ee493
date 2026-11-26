# MehmetAliAkinci

**Owner:** Mehmet Ali Akıncı
**Subsystem:** Localization, State Estimation and Sensor Fusion
**Related requirements:** Unverified - Proposal Report mapping pending.

## Responsibilities

Develop and validate robot pose, velocity, and sensor-state estimation using UWB localization, IMU characterization and calibration, Visual Odometry, Visual-Inertial Odometry, and Wheel Odometry. Investigate EKF and Error-State EKF, multi-sensor fusion, sensor fault detection, and localization simulation and validation. These are assigned work areas, not completed implementations.

## Current status

- The inspected personal-folder history contains the initial template entry dated 2026-11-14; no localization implementation or experimental results are recorded yet.
- Shared AI instructions, an English log template, and optional Codex/Claude lifecycle hooks are available. See [WORKFLOW.md](WORKFLOW.md) for activation, checks, and limits.
- [LOG.md](LOG.md) holds history; [AGENTS.md](AGENTS.md) holds common rules; [CLAUDE.md](CLAUDE.md) imports them for Claude Code.

## How to run

Localization software: **Not runnable yet.**

Work-record tooling requires Git and Python 3.9+. From this folder:

```text
python tools/worklog_guard.py check
python -m unittest discover -s tools -p "test_*.py" -v
```

Launch Codex or Claude Code from `MehmetAliAkinci/` and follow WORKFLOW.md to review/enable hooks. No global settings are installed.

## Open problems and next steps

- Verify FR mappings against the Proposal Report.
- Confirm sensor hardware, interfaces, coordinate frames, timestamp synchronization, calibration procedures, and available datasets with the team.
- Define accuracy, latency, robustness, and fault-detection acceptance criteria.
- Establish a reproducible simulation baseline, then document hardware measurements separately.

## Large files (Google Drive links)

No artifact links have been supplied. Store datasets, recordings, and model weights in the team Google Drive and add verified links here.
