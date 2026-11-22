# OmerFurkanDirier – Work Log

Newest entry at the top. Format is defined in [RULEBOOK.md](../RULEBOOK.md).

### 2026-11-22 – Stereo vs single camera on a single-CSI Pi 4; plan written
- **What I did:**
  - Re-read the RAPTOR project description for camera-related requirements.
  - Compared stereo hardware routes for the Pi 4 against single-camera geometry.
  - Created `pi_esp32_link/` as a placeholder for the Pi–ESP32 serial protocol (work on it later).
- **Decisions:**
  - **Decision:** Proceed with the single camera (Pi Camera V2, already owned) as the working solution. Revisit if single-camera obstacle detection turns out to be inadequate.
    **Alternatives considered:** Arducam CamArray synchronized stereo kit (about $165–260); ELP synchronized USB stereo board (about $80–84); Waveshare IMX219-83 (4,206 TL, needs two CSI ports, so unusable on Pi 4 as-is); OAK-D Lite ($269, does its own detection); two unsynchronized webcams (rejected: frame offset exceeds the signal).
    **Reason:** Total team budget is $350, reduced by about $80 equipment rent (so roughly $270 left for everything); we already own the Camera V2; by hand-calculation, ground-plane ranging gives similar accuracy to 60 mm-baseline stereo at 1–3 m. Caveat: that comparison used assumed pixel errors (0.5 px stereo, 2 px ground plane) and an estimated camera height (0.23 m), so it must be verified by measurement (plan step C3). Advisor will not allow ToF/ultrasonic sensors (user's reading), so obstacle detection must come from the camera.
- **Equipment (as of today):** Department supplied the Raspberry Pi 4 (4 GB) and one DWM3001CDK; BMI270 board is on the list, not received yet; Camera V2 is our own. The other four UWB anchors are set up by the course in a 10×10 m arena.
- **Plan:** Written to `PLAN.md` (camera steps C1–C5, communication steps K1–K5). Hüseyin Kerem Aktaş owns the detection model.
- **Results / measurements:** (public sources and my own calculations, not measurements)
  - Project text: camera must contribute to localization; target detect ≤2 s, reacquire ≤3 s, follow at safe distance; avoid obstacles. "External localization aids such as LiDAR, GPS, or additional ranging devices shall not be used."
  - Stereo depth error δZ = Z²·δd/(f·B). For 60 mm baseline, 73° HFOV, 640 px (f ≈ 432 px), δd = 0.5 px: 1.9 cm at 1 m, 7.7 cm at 2 m, 17 cm at 3 m, 48 cm at 5 m.
  - Single camera on a flat floor (ground plane): Z = f·h/(v − v_horizon). With camera height h ≈ 0.23 m (my estimate from Şevval's chassis numbers, to verify) and 2 px bounding-box error: 2.0 cm at 1 m, 8.0 cm at 2 m, 18 cm at 3 m, 50 cm at 5 m. Almost the same as stereo. Weak point: pitch error, δZ ≈ Z²·δθ/h (1.3° caster rocking gives about 40 cm at 2 m unless the IMU corrects it). Fails if the target's feet are hidden.
  - With h ≈ 0.23 m and 50° VFOV, a 1.7 m person is fully in view only beyond about 3.2 m.
  - Two unsynchronized webcams: up to 33 ms frame offset at 30 fps; turning at 1 rad/s shifts the image about 14 px, more than the 8.6 px true disparity at 3 m. Not usable.
  - Prices (USD/TRY 50.52, Wise, 2026-11-22; imports exclude shipping/customs):
    - Waveshare IMX219-83 (60 mm baseline, 73° HFOV, ICM20948 IMU): 4,206.07 TL incl. KDV at Robotistan, shown sold out. Needs two CSI ports.
    - Arducam CamArray stereo kits (one CSI port, hardware sync, Pi 4B listed): OV9281 mono global shutter $164.99 (~8,300 TL); AR0234 color $259.99 (~13,100 TL). 8MP IMX219 kit discontinued ($129.99).
    - Luxonis OAK-D Lite (75 mm baseline, on-device depth and AI, BMI270): $269 (~13,600 TL).
    - ELP synchronized USB stereo board (1.3 MP, side-by-side up to 2560×960 at 60 fps, MJPEG, USB 2.0): $80–84 (~4,050–4,250 TL). Only synchronized stereo option inside 5000 TL.
  - Raspberry Pi docs: libcamera has no stereo support; Pi 4 has one camera connector.
- **Problems / open questions:**
  - Is 5000 TL a hard limit for the camera? Do we already own a Pi Camera V2?
  - Advisor: are ToF/ultrasonic sensors allowed for obstacle avoidance only? Would a stereo camera count as a "ranging device"?
  - Team following distance (decides camera tilt).
  - Effect of H.264 compression on stereo matching on the PC: confirmed as a trade-off in literature, no numbers found; must measure.
  - Pi 4 vs Pi 5: Şevval's README and LOG say Raspberry Pi 5; we use Pi 4. Team must confirm which board is real (affects camera ports and H.264 hardware encoding).
  - Pi operating system (Raspberry Pi OS vs Ubuntu) is undecided; affects libcamera and ROS 2 setup.
  - What the PC sends back (proposal: timestamped detections, not motor commands) is not agreed.
  - Camera height and tilt not decided (my task); a person is fully in view only beyond about 3.2 m at 0.23 m height and 50° VFOV.
  - Following distance not decided by the team.
  - The ToF/ultrasonic ban is my reading of the advisor's view; worth confirming with him.
- **Next steps:** Follow PLAN.md: boot the Pi 4 with the chosen OS, get a frame from the Camera V2 (C1), and run iperf3/ping with power save off (K1). Raise Pi 4 vs 5 and the OS choice in the group chat. Study the reading list in PLAN.md; calibration and range exercises were skipped for now.

### 2026-11-18 – Wi-Fi link research and stereo camera options
- **What I did:** Researched whether the Pi 4 built-in Wi-Fi can stream the camera to a PC for offboard detection (FR5.1, FR5.2, FR2.3). Researched stereo camera options for the Pi 4 under a 5000 TL budget.
- **Decisions:** –
- **Results / measurements:** (all from public sources, not our own measurements)
  - Pi 4 Wi-Fi chip: 802.11ac, 2.4/5 GHz, 1x1, max 433.3 Mbit/s on air. Measured by others: 63.8–76.3 Mbit/s (5 GHz, iperf3, Tom's Hardware); 58–71 Mbit/s on a dedicated access point vs. 12.4 Mbit/s on a busy home router (dev.to ROS robot).
  - Pi 4 hardware H.264 encoder: 1080p30 max. YouTube guide bitrates: 480p30 4 Mbit/s, 720p30 8 Mbit/s. Raw 640×480×30 fps ≈ 221 Mbit/s, too large for the link.
  - Wi-Fi power save on: ping 175–1457 ms; off: about 10 ms (Linux kernel mailing list, Pi 4, 5 GHz).
  - Pi 4 has one CSI port, so IMX219-83 (two CSI cables) cannot be used directly. Multiplexer is one camera at a time. Arducam stereo/CamArray HAT merges two cameras but lists only Arducam camera kits; IMX219-83 support unconfirmed. USB UVC stereo boards (e.g., ELP-USB960P2CAM-V90, about $80 in 2023) are the practical alternative; no current Turkish price found.
- **Problems / open questions:** See README "Open problems". Delay for Pi 4 + Camera V2 over Wi-Fi not found in any source. DFRobot CG0328 specs conflict between sellers (0.3 MP VGA vs 2 MP).
- **Next steps:** Run iperf3 between Pi and PC across the full arena. Check and disable Wi-Fi power save. Decide router/access point. Ask Arducam/Waveshare whether IMX219-83 works with their HAT, or choose a USB stereo board. Check FR links to the Proposal Report.

### 2026-11-14 – Folder created
- **What I did:** Folder, README.md and LOG.md created from the team template.
- **Decisions:** –
- **Results / measurements:** –
- **Problems / open questions:** –
- **Next steps:** Fill in README.md (subsystem, related FR codes) and start logging work.
