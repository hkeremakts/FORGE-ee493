# SevvalNidaSagir – Work Log

Newest entry at the top. Format is defined in [RULEBOOK.md](../RULEBOOK.md).

### 2026-11-22 – Raspberry Pi 4 instead of Pi 5
- **What I did:**
  - Switched all my files from Raspberry Pi 5 to Raspberry Pi 4 (README, CAD names and comments, drawings, BOM). Ömer's and Güneş's logs had asked the team to confirm which board is used.
  - Switched the camera from Pi Camera 3 to Pi Camera V2, which the team already owns.
  - Regenerated the drawings, BOM and STEP files and re-ran the clash check.
- **Decisions:**
  - **Decision:** The robot uses the department-supplied Raspberry Pi 4 Model B (4 GB) as the high-level computer.
    **Alternatives considered:** Raspberry Pi 5 (my earlier assumption).
    **Reason:**
    - The department supplied the Pi 4 (see Ömer's log), and the Proposal Report (Table 7) already lists it.
    - It changes nothing mechanical: the Pi 4 and Pi 5 have the same 85 × 56 mm board and the same 58 × 49 mm M2.5 mounting holes.
    - The ESP32/Pi split stays the same: the Pi 4 also has only 2 hardware PWM channels and runs Linux.
    - Power gets easier: a Pi 4 needs 5 V / 3 A, so the XL4015 (5 A) is no longer marginal.
  - **Decision:** The mast-top camera plate stays as it is for the Pi Camera V2.
    **Alternatives considered:** Redesigning the plate.
    **Reason:** Camera V2 and Camera 3 have the same 25 × 24 mm board and the same 21 × 12.5 mm M2 hole pattern.
- **Results / measurements:**
  - Printed parts (STL) are unchanged. Only labels and names in the STEP, PDF and BOM changed.
  - Clash check still passes for both layouts.
- **Problems / open questions:**
  - The UWB board is a DWM3001CDK. Check that it fits the 48 × 48 mm UWB platform on the mast top, and measure its holes when it arrives.
  - FR codes still need to be linked.
- **Next steps:**
  - Agree on the Pi 4 ↔ ESP32 serial protocol with Ömer.
  - The steps from the 2026-11-18 entry still apply.

### 2026-11-18 – Drive system design, parts selection and 3D-printed chassis (v2)
- **What I did:**
  - Chose the drive layout, motor, motor driver, controller split, wheels and casters.
  - Designed a parametric 3D-printed chassis (CadQuery) with dimensioned drawings, BOM and clash check.
  - Wrote my section of the Week 8 progress report.
  - Wrote first ESP32 encoder and motor-control sketches (for a Cytron MDD3A).
  - Started ordering parts.
- **Decisions:**
  - **Decision:** Differential drive (2 driven wheels + ball casters).
    **Alternatives considered:** Ackermann steering.
    **Reason:** Can turn in place, which helps keep the target in the camera's view. Simple kinematics and odometry for UWB/IMU fusion. Ackermann cannot turn in place.
  - **Decision:** The same plates support two layouts. B (preferred): wheels in the middle, casters at front and back (y = ±88 mm). A: wheels at the front (axle at y = +62 mm), one rear caster.
    **Alternatives considered:** A single fixed layout.
    **Reason:** B rotates about the plate center, where the camera mast is. A is more stable against tipping and needs only one caster. Supporting both costs only a second set of bracket holes and a second mast socket. In B, one caster is set 1–2 mm high so the robot does not rock.
  - **Decision:** Motor JGB37-520, 12 V, 530 rpm, 1:19, Hall encoder (2 + 1 spare, Direnc.net, 665.41 TL each).
    **Alternatives considered:** N20 micro-gear motors; 330 rpm and 1000 rpm JGB37 versions; Pololu 25D/37D (out of stock / expensive); ungeared motors.
    **Reason:**
    - Meets my criteria: > 300 rpm, about 1 m/s, 2–2.5 kg robot, 12 V (3S battery), 2-channel encoder, stall > 2 A, available in Turkey.
    - Rated 2.2 kg·cm at 407 rpm, stall 3.1 kg·cm / 2.3 A.
    - N20 motors have too little torque. 1000 rpm gives poor low-speed control and less torque. 330 rpm leaves little speed margin.
  - **Decision:** BTS7960B (IBT-2) driver, one board per motor (Robotzade, 275.40 TL).
    **Alternatives considered:** Cytron MDD3A, TB6612FNG, DRV8874, L298N.
    **Reason:**
    - Large current margin (20 A continuous vs 2.3 A stall).
    - Current-sense outputs.
    - 3.3 V logic compatible, in stock.
    - TB6612 is close to its current limit at stall; L298N drops ~2 V; DRV8874 was not in stock. The MDD3A used in the first sketches has no current sensing.
    - It drives brushed DC motors. A shop note saying otherwise is a typo; the Infineon datasheet confirms it. It has no reverse-polarity protection.
  - **Decision:** ESP32 DevKit V1 does the low-level motor control; Raspberry Pi 5 does the high-level work and sends commands over USB serial.
    **Alternatives considered:** Motors and encoders directly on the Raspberry Pi.
    **Reason:** About 12k encoder edges/s at top speed. The ESP32 hardware counter (PCNT) never misses them; Linux on the Pi can. The Pi also has only 2 hardware PWM channels and we need 4.
  - **Decision:** Wheels 65 × 27 mm smooth rubber (Motorobit) + 6 mm hex coupling (12 mm hex, 30 mm long).
    **Alternatives considered:** 80 mm (design v1, not in stock); 85 × 38 / 85 × 32 off-road wheels; self-printed wheels.
    **Reason:**
    - All 85 mm options found have spiky treads: vibration, worse odometry.
    - The arena is a flat indoor floor, so 14.5 mm ground clearance is acceptable.
    - Smaller wheel: ~23% more push force, finer odometry (~0.24 mm/count).
    - Top speed ~1.7 m/s at 11.1 V, target 1 m/s.
    - Trade-off: obstacles over ~1 cm block the robot.
  - **Decision:** Pololu #953 casters (1/2" metal ball, 13.5 mm) + 1 mm printed shim.
    **Alternatives considered:** Pololu #955 3/4" (20.8 mm) mounted through the plate; W420 (20 mm); Pololu 3/8" #951.
    **Reason:**
    - Plate bottom = wheel radius − 18 mm = 14.5 mm, so the caster must be ≤ 14.5 mm tall.
    - #955 has no flange. Mounting it through the plate needs a 6 mm boss that collides with the battery/driver area.
    - #953 mounts flat under the plate, load 1–1.5 kg each.
  - **Decision:** 3D-printed PETG chassis:
    - Two 136 × 210 × 5 mm plates, 55 mm apart, 6 M3 pillars.
    - 5 mm motor brackets with 6 arc slots.
    - 15 mm M3 grid for modules.
    - 150 mm camera/UWB mast.

    **Alternatives considered:** Ready-made acrylic/aluminum robot kits; PLA; metal L-brackets.
    **Reason:**
    - Fits our exact motors and layouts, prints on a 220 × 220 mm bed, cheap to iterate.
    - PETG instead of PLA because motors reach 40–50 °C and PLA creeps.
    - Bracket stress ~3 MPa, well below PETG layer strength.
    - The arc slots accept any motor hole angle.
  - **Decision (power, with Güneş):** Keep the team's 3S Li-ion pack (3 × Samsung 25R 18650 + BMS).
    **Alternatives considered:** 3S LiPo.
    **Reason:** Already bought, fits the 12 V motors (12.6 V full / 11.1 V nominal) and fits on the bottom deck. Battery voltage is monitored on the ESP32 through a 100k/22k divider, with a software cutoff around 9.9 V.
- **Results / measurements:**
  - CAD clash check passes for both layouts: motor to plate 1.5 mm, motors 9 mm apart, wheel to plate edge ~10 mm.
  - Overall: 211 × 210 mm, height ~278 mm, camera center ~262 mm, ground clearance 14.5 mm.
  - No measurements on real hardware yet.
- **Problems / open questions:**
  - Confirm the wheel/coupling fit with Motorobit.
  - The real motor hole angle and encoder counts per revolution are unverified (datasheet values only).
  - The XL4015 is marginal for the Pi 5.
  - The 3S charger and fuses are not bought yet.
  - FR codes still need to be linked.
- **Next steps:**
  1. Order wheels, couplings, casters and screws. Solder the ESP32 headers.
  2. Print one bracket and test-fit the motor, then print the rest.
  3. Port the firmware to BTS7960 and update its constants. Tune the wheel PID and odometry. Define the serial protocol with the Pi.
  4. When UWB ranges are available, compute the robot's 2D position (x, y).

### 2026-11-14 – Folder created
- **What I did:** Folder, README.md and LOG.md created from the team template.
- **Decisions:** –
- **Results / measurements:** –
- **Problems / open questions:** –
- **Next steps:** Fill in README.md (subsystem, related FR codes) and start logging work.
