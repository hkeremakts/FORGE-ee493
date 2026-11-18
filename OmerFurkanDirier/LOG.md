# OmerFurkanDirier – Work Log

Newest entry at the top. Format is defined in [RULEBOOK.md](../RULEBOOK.md).

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
