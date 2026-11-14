# FORGE – RAPTOR Rulebook

This file defines how every team member (and their AI assistant) works in this repository.
Read it fully before making any change.

## Repository structure
- `/<MemberName>/` – personal folder. Only its owner changes it.
- `/shared/` – interfaces and code used by more than one subsystem
  (e.g., ROS 2 messages, common configs). Changes here must be announced to the team.
- Root files (`RULEBOOK.md`, `README.md`, `GUIDE.md`, `.gitignore`) – changed only by the team leader.

## Folder ownership
| Folder | Owner |
|---|---|
| HuseyinKeremAktas | Hüseyin Kerem Aktaş |
| MehmetAliAkinci | Mehmet Ali Akıncı |
| OmerFurkanDirier | Ömer Furkan Dirier |
| GunesCeylan | Güneş Ceylan |
| SevvalNidaSagir | Şevval Nida Sağır |
| FurkanOnur | Furkan Onur |

## Rules
1. Work only inside your own folder. Never edit another member's folder.
2. Every folder contains:
   - `README.md` – the current state: what this part does, how to run it, open problems. Keep it short and up to date.
   - `LOG.md` – dated entries, newest at the top.
3. After every work session, add a `LOG.md` entry and update `README.md` if the state changed.
4. Record every decision in this format:
   **Decision:** … **Alternatives considered:** … **Reason:** …
5. Do not commit large files (datasets, videos, model weights, files > 50 MB).
   Store them in the team Google Drive and put the link in your README.
6. Commit messages: `[MemberName] short description of the change`.
7. Before changing `/shared/`, tell the team in the group chat.

## Git workflow (local copy ↔ GitHub)
1. Start of every session: `git pull` to get everyone's latest changes.
2. Work only in your own folder (and in `shared/` only after telling the team).
3. Stage only your own folder: `git add <YourFolder>/`
   (never `git add .` from the root, so you don't commit someone else's files by accident).
4. Commit: `git commit -m "[YourFolder] short description"`
5. Push: `git push`. If the push is rejected, run `git pull` first, then push again.
6. Never use `git push --force`.
7. Push at least once at the end of every work session, so the team always sees your latest state.

## LOG.md entry format
```
### YYYY-MM-DD – Short title
- **What I did:** …
- **Decisions:** (use the decision format above)
- **Results / measurements:** …
- **Problems / open questions:** …
- **Next steps:** …
```

## Project references
- Requirements (FR codes, constraints): Proposal Report, Requirement Analysis section
- Schedule and milestones: Proposal Report, Gantt chart
- Link every task, test and decision to an FR code where possible (e.g., FR4.2).
