# FurkanOnur – Work Log

Newest entry at the top. Format is defined in [RULEBOOK.md](../RULEBOOK.md).

### 2026-11-24 – Repository setup, UWB research and ground station planning
- **What I did:** Set up repository access and my AI workspace. Filled in README with subsystem, related FR codes (FR5.1, FR5.2, FR2.5, FR2.3) and work package T11. Researched how the UWB anchors and tag communicate and work, as support for Mehmet Ali (Localization). Started thinking about the ground station platform.
  - Researched how UWB works, how the anchors communicate with the tag, and the possible communication methods. Prepared a pros/cons comparison of these methods, to be discussed with Mehmet Ali (Localization) and Şevval.
  - Researched camera options for the robot.
- **Decisions:** None yet.
- **Results / measurements:**
  - Camera: identified 3 risks with the provided camera (Raspberry Pi Camera Module v2):
    - (1) At distances below 1 m, a person may not fit in the field of view. This is relevant to FR3.3: the following distance is 1.0–2.0 m, but the minimum allowed distance is 0.7 m, so the risk can occur when the robot is between 0.7 m and 1 m from the target.
    - (2) Rolling shutter: the image may skew and distort while the robot rotates 360°. This is relevant to FR4.1 (360° scan ≤ 10 s). Choosing the rotation speed within this limit may reduce the distortion; to be discussed with the team.
    - (3) Noise increases in low light.
  - A stereo camera only adds depth perception; it carries the same 3 risks as the provided camera.
  - Alternative mono camera: Raspberry Pi Camera Module 3 Wide. It eliminates risks (1) and (3) without extra hardware; risk (2) remains, as it is also rolling shutter.
  - Preliminary recommendation (not yet discussed with the team): continue with the provided Camera Module v2, and switch to the Camera Module 3 Wide if one of these risks causes a problem in testing.
- **Problems / open questions:** (1) Web-based interface or desktop application for the ground station? (2) The communication method with the robot is not defined yet (with Ömer); camera choice depends on the link bandwidth (to be agreed with Ömer and Kerem).
- **Next steps:** Agree on the communication method and its bandwidth with Ömer. Select the camera together with Ömer and Kerem. Compare web-based and desktop options against FR5.1 and FR5.2, then decide.
  - Discuss the UWB communication options with Mehmet Ali and Şevval.
  - Discuss the camera recommendation with the team (Kerem, Ömer), including the rotation speed for the 360° scan.

### 2026-11-14 – Folder created
- **What I did:** Folder, README.md and LOG.md created from the team template.
- **Decisions:** –
- **Results / measurements:** –
- **Problems / open questions:** –
- **Next steps:** Fill in README.md (subsystem, related FR codes) and start logging work.
