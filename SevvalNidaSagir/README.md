# SevvalNidaSagir

**Owner:** Şevval Nida Sağır
**Subsystem:** Vehicle Motion – drive system, 3D-printed chassis, low-level motor control (ESP32: encoders, wheel-speed PID, odometry)
**Related requirements:** _FR codes to be added from the Proposal Report (Requirement Analysis)_

## What this part does
Moves the robot. It is a differential-drive base: two JGB37-520 12 V encoder motors, each driven by a BTS7960 board, with Pololu ball casters. An ESP32 counts the encoders, runs a PID speed loop for each wheel and computes odometry. It takes speed commands from the Raspberry Pi 4 over USB serial; the protocol is being defined with Ömer in `OmerFurkanDirier/pi_esp32_link/`. The 3D-printed PETG chassis has two decks and a camera/UWB mast. The top plate takes the Pi 4 (58 × 49 mm, M2.5 holes) and the mast top takes the Pi Camera V2 (21 × 12.5 mm, M2 holes). The same plates support two wheel layouts (A: wheels at the front, B: wheels in the middle).

## Folder contents
| Path | What |
|---|---|
| `docs/RAPTOR_chassis_drawings_v2.pdf` | Dimensioned drawings (9 pages): overall size, layouts A/B, plates, bracket, motor, BOM |
| `docs/RAPTOR_drive_BOM_v2.xlsx` | Bill of materials with links, status and price formulas |
| `docs/RAPTOR_Motor_Secenekleri.pdf` | Motor options comparison (Turkish shops) |
| `chassis/stl/` | Print-ready parts (all fit a 220 × 220 mm bed) |
| `chassis/step/` | Same parts and both assemblies (`montaj_A/B.step`) for editing in CAD |
| `chassis/motor_model/` | JGB37-520 3D model (STEP/STL, drawn from the datasheet) |
| `chassis/cad/` | Parametric CadQuery source and scripts for drawings, BOM and clash check |
| `firmware/legacy_mdd3a/` | First encoder test and motor-control sketches (written for a Cytron MDD3A, being ported to BTS7960) |

## How to run it
- **Chassis:** print the STL files in PETG. Print settings and assembly order are in the drawings PDF.
- **Regenerate CAD:**
  ```
  pip install cadquery
  cd chassis/cad
  python3 raptor_chassis.py   # writes out/
  python3 check.py            # clash check
  ```
- **Firmware:** not runnable on the final hardware yet. The legacy sketches need Arduino IDE with ESP32 core 3.x and the `ESP32Encoder` library.

## Current status
- **Design v2 frozen:**
  - Wheels: 65 × 27 mm smooth rubber, 6 mm hex coupling.
  - Casters: Pololu #953 (1/2" metal ball).
  - Ground clearance 14.5 mm, track 184 mm, total width ~211 mm.
- **Parts:**
  - Motors ordered.
  - BTS7960 ×2, ESP32 and wire being ordered.
  - Wheels, couplings and casters to buy.
- **Firmware:** must be ported from MDD3A to BTS7960, and these constants updated:
  - counts per wheel revolution 1320 → ~836 (1:19 gearbox; to verify on the real motor)
  - wheel diameter 0.085 → 0.065 m
  - wheel separation 0.20 → 0.184 m

## Open problems
- Confirm that the 65 × 27 wheel hub accepts the 6 mm hex coupling.
- Measure on the real parts: motor hole angle, wheel offset, encoder counts per revolution.
- The 3S charger and fuses are still missing (power subsystem).

## Large files (Google Drive links)
- None yet.
