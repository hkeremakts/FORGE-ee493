# Work records and agent setup

## Start here

Open a terminal in `MehmetAliAkinci/`. Use Python 3.9+ as `python` and Git on PATH.
Start Codex with `codex` here (or `codex -C MehmetAliAkinci` from the repository root).
For Claude Code, run `claude --settings .claude/settings.json` here to explicitly load the personal settings. CLAUDE.md imports AGENTS.md using `@AGENTS.md`.

Codex discovers the nested `.codex/hooks.json` when this directory is in its project-to-working-directory path. Review and trust the project and hooks using `/hooks` or the desktop hook review UI. New/changed hooks may require review again. Do not bypass hook trust. For Claude, inspect `/hooks` and complete any project trust or hook review required by that installation. Restart the agent after setup and verify that SessionStart reports its pull result.

Starting at the repository root does not guarantee discovery of personal instructions/settings. Prefer starting here. Do not copy these hooks to global/root configuration: duplicate registrations can run twice and root edits are outside this task's scope. No global configuration or Git hooks are installed.

## Automation and boundaries

| Mechanism | Behavior | Limit |
| --- | --- | --- |
| AGENTS.md / CLAUDE.md | Instruct the agent to read context, document each task, update state, and complete scoped Git work | Agent compliance, not an operating-system enforcement boundary |
| SessionStart command hook | Runs `git pull --ff-only`; injects startup instructions; ignores repeat successful startup calls for the same session ID | Requires loaded/trusted hooks, Git/network/authentication; failure is reported to the agent, not silently treated as success |
| Stop command hook | Requests one documentation/completion review per turn and reports guard findings | `stop_hook_active` prevents loops; this is a bounded reminder, not a hard gate or semantic proof |
| Guard `check` | Checks preservation of HEAD log entries, duplicate IDs, all staged paths, and files over 50 MB | Does not detect every paraphrased duplicate, verify measurements, or replace staged diff review |
| Agent closeout | Writes English records and performs authorized scoped commit/push | Credentials, platform approvals, conflicts, and protected branches can block it |
| External ChatGPT/AI | Uses the same record template and source ID | Without repository access, a human or connected agent must transfer the record and perform Git operations |

Hooks never generate experimental claims, append generic log entries, or run commit/push themselves. Task documentation includes research without file changes. The agent judges what is meaningful and checks for equivalent records before inserting. A normal Stop is a turn boundary; it is not necessarily the end of the whole session. Forced termination, disabled hooks, missing Python, or an unavailable agent cannot guarantee closeout. Document interrupted work when resuming.

Startup markers live only in ignored `.worklog-state/`, keyed by a hash of the session ID. A failed pull creates no success marker; retry after resolving the issue. If a host omits session IDs, startup deduplication is unavailable. Parallel editing sessions in the same checkout are unsupported; coordinate them to avoid overwriting records.

## Log template

Insert below the introduction and above older entries. Use the actual work date (local timezone Europe/Istanbul), not an invented date. An imported entry uses its import date as the heading and records the original work date separately. Preserve old entries, including the legacy template entry.

```markdown
### YYYY-MM-DD - Short title
- **Record ID:** unique-stable-task-or-source-id
- **Source:** Local / Codex / Claude Code / ChatGPT / other; work date; source reference or "not supplied"; import date if applicable.
- **Requirements:** Verified FR code and source, or "Unverified - Proposal Report mapping pending".
- **What I did:** Concrete scope and relevant files/artifacts.
- **Decisions:**
  - **Decision:** ... **Alternatives considered:** ... **Reason:** ...
- **Results / measurements:**
  - **Observed:** Executed checks or hardware measurements, commands, conditions, units, evidence; or "Not performed".
  - **Simulation:** Conditions and results, or "Not performed".
  - **Theoretical expectations:** Explicitly labelled expectations, or "Not assessed".
  - **Unverified imported claims:** Source claims pending verification, or "None".
- **Problems / open questions:** Failures, limitations, unresolved mappings.
- **Next steps:** Specific follow-up work.
```

Use "No engineering decision made" when appropriate; do not invent alternatives for a task that made no decision. Repeat the three-part decision item for each actual decision. IDs identify tasks/sources, not each invocation of an AI. For external summaries, search both the ID and the source/task description; a different ID alone does not make the same work new. Do not store private chat links or sensitive transcripts unnecessarily.

## Validation and Git closeout

From this directory:

```text
python -m unittest discover -s tools -p "test_*.py" -v
python tools/worklog_guard.py check
git diff --check
git diff -- ../MehmetAliAkinci/
```

Review new/untracked files too. Stage explicit personal paths, inspect the entire staged diff and run the guard again. Use `[MehmetAliAkinci] short description`. Before pushing, inspect all outgoing commits and their paths, including commits not created this session. Do not include unrelated staged changes or force push. Preserve both sides of conflicting log entries; report unresolved conflicts and authentication/permission failures. See AGENTS.md for the full sequence.

Tests exercise the hook protocol directly and mock pull failures/retries and invalid staged scope. They do not prove an installed agent has loaded/trusted the hooks. Verify real hook activation in the host UI on the next session. The setup machine has Codex CLI 0.153.4; Claude Code was not found on PATH during setup, so Claude runtime loading is unverified.

## Official references checked during setup (2026-11-26)

- [Codex instructions](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)
- [Codex lifecycle hooks and trust](https://learn.chatgpt.com/docs/hooks)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code memory imports](https://code.claude.com/docs/en/memory)
- [Claude Code settings](https://code.claude.com/docs/en/settings)
