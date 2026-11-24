# FurkanOnur – Work Log

Newest entry at the top. Format is defined in [RULEBOOK.md](../RULEBOOK.md).

### 2026-11-24 – README filled in, project context reviewed
- **What I did:** Read RULEBOOK.md, the root README and the teammates' READMEs/LOGs that mention the GUI, ground station or e-stop. Filled in my README: subsystem, roles, related FR codes, what my part does, open problems.
- **Decisions:**
  - **Decision:** List FR5.1, FR5.2, FR2.3, FR2.5 and C10 as my related requirements, marked "to be checked against the Proposal Report".
    **Alternatives considered:** Leave the field empty until I read the report again; list only FR5.1/FR5.2.
    **Reason:** These codes already appear in Ömer's and Güneş's READMEs with my name attached to the GUI e-stop, so they are the best current info; marking them unchecked avoids copying an error silently.
  - **Decision:** The GUI's scope stops at the PC side; the data links (camera stream, telemetry, e-stop path) belong to Communication (Ömer).
    **Alternatives considered:** UI subsystem also owns the PC-side network code.
    **Reason:** Matches Ömer's README ("telemetry to the GUI, and the e-stop path"); avoids two people building the same link.
- **Results / measurements:** –
- **Problems / open questions:** GUI framework not chosen. Message format for telemetry/commands not agreed with Ömer yet (probably goes to `/shared/`, needs a team announcement first).
- **Next steps:** Check FR codes in the Proposal Report. Compare GUI framework options. Agree the telemetry/command interface with Ömer.

### 2026-11-14 – Folder created
- **What I did:** Folder, README.md and LOG.md created from the team template.
- **Decisions:** –
- **Results / measurements:** –
- **Problems / open questions:** –
- **Next steps:** Fill in README.md (subsystem, related FR codes) and start logging work.
