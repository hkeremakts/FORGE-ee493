"""Local lifecycle support. Never invent log entries or commit/push from hooks."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

PERSONAL = Path(__file__).resolve().parents[1]
ROOT = PERSONAL.parent
PREFIX = "MehmetAliAkinci/"
LIMIT = 50_000_000


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                          timeout=45, check=False)


def text(result):
    return result.stdout.decode("utf-8", errors="replace")


def log_errors(current, previous):
    errors = []
    # Git may convert LF/CRLF on checkout; compare content without that conversion.
    current = current.replace(b"\r\n", b"\n")
    previous = previous.replace(b"\r\n", b"\n")
    for entry in re.split(rb"(?m)(?=^### )", previous)[1:]:
        if entry not in current:
            errors.append("Existing LOG history was removed or modified; restore it verbatim.")
            break
    ids = re.findall(rb"(?m)^- \*\*Record ID:\*\*\s*(\S+)", current)
    if len(ids) != len(set(ids)):
        errors.append("Duplicate Record ID in LOG.md.")
    return errors


def check():
    errors = []
    old = git("show", "HEAD:" + PREFIX + "LOG.md")
    if old.returncode:
        errors.append("Cannot read baseline LOG from HEAD; inspect Git state.")
    else:
        errors.extend(log_errors((PERSONAL / "LOG.md").read_bytes(), old.stdout))
    staged = git("diff", "--cached", "--name-only", "--no-renames", "-z")
    if staged.returncode:
        errors.append("Cannot inspect staged paths.")
    else:
        for path in text(staged).split("\0"):
            if not path:
                continue
            if not path.startswith(PREFIX):
                errors.append("Out-of-scope staged path: " + path)
                continue
            if path == PREFIX + "LOG.md":
                indexed = git("show", ":" + path)
                if indexed.returncode:
                    errors.append("LOG.md must not be deleted from the index.")
                elif old.returncode == 0:
                    errors.extend(log_errors(indexed.stdout, old.stdout))
            size = git("cat-file", "-s", ":" + path)
            # Deleted paths have no index blob.
            if size.returncode == 0 and int(size.stdout) > LIMIT:
                errors.append("Staged file exceeds 50 MB: " + path)
    for path in PERSONAL.rglob("*"):
        if path.is_file() and not path.is_symlink() and ".worklog-state" not in path.parts:
            if path.stat().st_size > LIMIT:
                errors.append("Local file exceeds 50 MB; keep outside Git: " + str(path.relative_to(ROOT)))
    return errors


def start(payload):
    session = str(payload.get("session_id", ""))
    state = PERSONAL / ".worklog-state"
    marker = state / (hashlib.sha256(session.encode()).hexdigest() + ".started")
    if session and marker.exists():
        result = "Startup pull already succeeded for this session; do not repeat it."
    else:
        pulled = git("pull", "--ff-only")
        detail = (text(pulled) + pulled.stderr.decode("utf-8", errors="replace")).strip()
        if pulled.returncode == 0:
            result = "Startup git pull --ff-only succeeded. " + detail
            if session:
                state.mkdir(exist_ok=True)
                marker.write_text("success\n", encoding="utf-8")
        else:
            result = "STARTUP PULL FAILED. Preserve work, report and resolve before dependent edits. " + detail
    return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext":
        result + " Fully read MehmetAliAkinci/AGENTS.md, RULEBOOK.md, GUIDE.md, "
        "MehmetAliAkinci/README.md and MehmetAliAkinci/LOG.md before working. "
        "Only author changes inside MehmetAliAkinci/."}}


def stop(payload):
    # One continuation per turn, never an infinite stop/log loop.
    if payload.get("stop_hook_active"):
        return {}
    errors = check()
    reason = ("Complete the AGENTS.md documentation check before finishing: record any "
              "unlogged meaningful work in English using WORKFLOW.md; preserve history; "
              "reuse existing task/source IDs and do not duplicate entries. Update README "
              "only if state changed. If nothing new happened, do not write an empty log. "
              "At session end inspect staged/outgoing scope, commit and push within permissions, "
              "and report actual outcomes or blockers. This reminder is not a request for new work.")
    if errors:
        reason += " Guard findings: " + " | ".join(errors)
    return {"decision": "block", "reason": reason}


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        errors = check()
        print("\n".join(errors) if errors else "PASS: history, record IDs, staged scope and size checks.")
        return bool(errors)
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("Expected a hook JSON object")
        event = payload.get("hook_event_name")
        output = start(payload) if event == "SessionStart" else stop(payload) if event == "Stop" else {}
        print(json.dumps(output))
        return 0
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print("Worklog hook failed; follow AGENTS.md manually: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
