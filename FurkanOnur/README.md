# FurkanOnur

**Owner:** Furkan Onur
**Subsystem:** User Interface and Ground Station (lead). Member of Power Management and Motion Control.
**Related requirements:**
- FR5.1 Display robot, sensor and tracking status (≥ 5 Hz, latency < 0.5 s)
- FR5.2 Accept operator commands and emergency stop (e-stop < 0.5 s)
- FR2.5 Stop safely or return to the safe zone
- FR2.3 Tolerate communication packet loss (≤ 2 s), shared with Communication
- Support: FR3.1–FR3.3 (Motion Control), C10 30-min mission (Power Management)
- Work package: T11 Communication, mission, GUI

## What this part does
The ground station GUI shows the robot position, target track, sensor health, mission status and faults in real time. It logs data and lets the operator set up the mission, send commands and trigger an emergency stop.

## How to run it
Not runnable yet.

## Current status
Early concept stage. Researched UWB communication methods (pros/cons list ready for discussion) and camera options (preliminary recommendation ready, not yet discussed with the team). Ground station platform (web vs. desktop) not decided yet. No code yet.

## Open problems
- Platform choice for the ground station GUI (web-based vs. desktop app).
- Robot–ground station communication method is not defined yet (with Ömer, Communication). Camera choice depends on it, since the link bandwidth limits the video that can be streamed to the ground station. To be agreed with Ömer and Kerem (Target and Obstacle Detection).

## Large files (Google Drive links)
- _Datasets, videos, model weights: link them here, never commit them._
