# Shared working instructions - FORGE / RAPTOR

Owner: Mehmet Ali Akinci. Subsystem: Localization, State Estimation and Sensor Fusion.
These rules apply to Codex, Claude Code, and work imported from other AI tools.
Start agents in this directory. If starting at the repository root, explicitly read this file first.

## Session startup

1. Inspect Git status; preserve existing work. Run `git pull --ff-only` at every new session (if SessionStart already ran it, inspect its result instead of repeating it). On failure, report the reason and resolve it before dependent edits. Never automatically stash, reset, or discard work.
2. Fully read `../RULEBOOK.md`, `../GUIDE.md`, `README.md`, and `LOG.md`. Re-read changed instructions after pulling. Inspect relevant files and Git history before making claims about previous work.
3. Author changes only inside `MehmetAliAkinci/`. Pulling team updates is expected. Do not edit root files, shared files, other members' folders, or global agent/Git configuration.

## Engineering and evidence

- Scope: UWB localization; IMU characterization/calibration; Visual Odometry; Visual-Inertial Odometry; Wheel Odometry; EKF and Error-State EKF; multi-sensor fusion; sensor fault detection; localization simulation and validation.
- Keep all records in English. Record every engineering decision as **Decision:** / **Alternatives considered:** / **Reason:**.
- Separate measured hardware results, simulation results, theoretical expectations, and unverified imported claims. Include commands, conditions, units, sources, and limitations as applicable. Never claim an unperformed test passed.
- Verify FR codes against the Proposal Report. Otherwise write `Unverified - Proposal Report mapping pending`; never copy example codes as actual mappings.
- Do not commit datasets, videos, model weights, or files larger than 50 MB. Store large artifacts in the team Google Drive and add verified links to README.

## Documentation after each task and at session end

- Immediately after each meaningful technical task (research, design, implementation, failed experiment, or imported summary), prepend a dated entry below the LOG introduction, newest first. Use WORKFLOW.md's template and a stable unique Record ID.
- Preserve existing LOG history verbatim. Corrections are new entries referencing the original ID.
- Search LOG for the ID and equivalent task/source before inserting. Reuse a source ID on re-import; never duplicate an existing record. New findings get a new ID and reference the prior entry.
- Update README when current implementation, setup, evidence, blockers, or next steps change.
- At every session end, ensure all work and unresolved outcomes are recorded. Task entries already satisfy session documentation: add only missing information, never a duplicate session summary or a log about writing the log. No empty entries for conversations without project work.
- Imported ChatGPT/other AI summaries use the same template: source tool/date/reference, import date, evidence status, decisions, open questions, and next steps. Mark unsupported claims unverified. Do not equate another AI's assertion with an observed experiment.
- Without repository access, provide the entry and README changes for transfer and state that files/Git were not updated.
- Run `python tools/worklog_guard.py check`, inspect the full diff, and verify historical entries remain intact. Hooks support this workflow; they cannot prove narrative truth/completeness. Follow the rules even without hooks.

## Git completion

- Never use `git add .`. Stage explicit paths under `MehmetAliAkinci/` only.
- Inspect `git diff --cached --name-only` and `git diff --cached`. If unrelated changes are staged, do not commit or unstage them; report the blocker.
- Run the guard again after staging. Commit as `[MehmetAliAkinci] short description`.
- At session end commit and push within available permissions. Ordinary scoped commits/pushes are authorized by this workflow; do not repeatedly ask for permission already granted. Respect actual tool approval/authentication requirements.
- Before push inspect status, upstream, and all outgoing commits (`git log @{upstream}..HEAD`) and their paths. Do not push unrelated local commits without authorization. Never force push.
- On rejection, pull safely and recheck before retrying. On divergence/conflicts, preserve all records and user work; report the issue and ask for help when resolution is uncertain. Never resolve LOG by discarding an entire side.
- Final response must state actual validation and commit/push outcomes. Never claim a successful push before observing it. Do not create a recursive log/commit merely to record the previous push.
