# Camera and communication plan (single camera, Pi 4)

Drafted 2026-11-22. Working plan, not final. Update it as results come in.
Related requirements: FR4.2, FR4.3, FR5.1, FR5.2, FR2.3, FR2.5.

## Phase 0: team decisions that block both tracks
1. **Pi operating system: Raspberry Pi OS or Ubuntu?**
   - camera_ros docs: Raspberry Pi OS ships the Raspberry Pi fork of libcamera; on Ubuntu that fork must be built from source.
   - ROS 2 binaries target Ubuntu.
   - Whether the Camera V2 works with upstream libcamera is untested. Test it, do not assume.
2. **What does the PC send back?** Proposal (not decided): detections with timestamps (box, class, confidence, capture time), not motor commands. Safety logic stays on the robot so it still works during a Wi-Fi outage (FR2.3, FR2.5).
3. **Detection model owner:** Hüseyin Kerem Aktaş.

## Camera track
| Step | What | Done when |
|---|---|---|
| C1 | Bring up Camera V2 on the Pi 4 at 640×480@30 and 1280×720@30 | Frames captured. Checked whether each mode uses the full sensor or a crop (a crop changes f). |
| C2 | Calibrate with an OpenCV checkerboard at the streaming resolution | K and distortion coefficients saved. Expect f near 530 px at 640 px wide (62.2° HFOV), if the mode is not cropped. |
| C3 | Ground-plane range test with a target at tape-measured 1, 2, 3, 4, 5 m | Table of measured errors. Replaces the assumed 2 px bounding-box error. |
| C4 | Choose camera height and tilt using the formulas and C3 results | Decision recorded in LOG.md. Mast belongs to Şevval's folder: coordinate with her. |
| C5 | Glass-to-glass latency (camera films a running stopwatch, compare with PC display) | A number, checked against FR4.2 and FR5.1. |

## Communication track
| Step | What | Done when |
|---|---|---|
| K1 | Dedicated 5 GHz router, Wi-Fi power save off, iperf3 and ping across the arena. Ask whether we may bring our own router. | Measured throughput and ping, including worst case. |
| K2 | Hardware H.264 from Pi to PC over UDP/RTP (GStreamer). Compare 2–3 transports with the stopwatch method. | One transport chosen, with measured latency. |
| K3 | Clock sync Pi and PC (chrony), capture timestamp on every frame | Per-frame delay known. |
| K4 | Return channel for detections: ROS 2 over Wi-Fi (best-effort QoS or rmw_zenoh) vs plain UDP | Latency and loss measured under a simulated outage. |
| K5 | Later: heartbeat/watchdog (FR2.3, FR2.5), e-stop (FR5.2), Pi–ESP32 protocol (`pi_esp32_link/`) | – |

Suggested order: C1 + K1 on the first hardware day, then C2 + K2, then C3 and C5.
First concrete step: boot the Pi 4 with the chosen OS and get one frame from the camera.

## Reading list
- EE493 slides "Image Analysis for Engineering Design", slides 27–36 (pinhole, homography, two cameras)
- First Principles of Computer Vision (Nayar): https://fpcv.cs.columbia.edu/Monographs (Image Formation, Camera Calibration, Uncalibrated Stereo)
- Szeliski, Computer Vision: Algorithms and Applications, 2nd ed.: https://szeliski.org/Book/
- OpenCV calibration tutorial: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
- Pi stream latency comparison (Pi 5, so encoder differs): https://www.hackster.io/eugene-tkachenko/comparing-video-stream-latencies-raspberry-pi-5-camera-v3-6c0ee4
- ROS 2 over Wi-Fi, multicast and IGMP snooping: https://discourse.openrobotics.org/t/ros2-wifi-multicast-multi-robot-and-igmp-snooping/28516
- rmw_zenoh: https://github.com/ros2/rmw_zenoh
- camera_ros: https://github.com/christianrauch/camera_ros
