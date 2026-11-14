# How to Join and Use the FORGE Repository

This guide gets you from zero to your first push. Takes about 15 minutes.
The rules themselves are in [RULEBOOK.md](RULEBOOK.md); this file is only about **how** to work.

---

## 1. One-time setup

### 1.1 GitHub account and invite
1. Create a GitHub account (if you don't have one) and send your username to Kerem.
2. Kerem adds you as a collaborator. You'll get an email / GitHub notification:
   **accept the invite**, otherwise you can't push.

### 1.2 Install Git (pick ONE option)

**Option A – GitHub Desktop (easiest, no terminal)**
1. Download from https://desktop.github.com and sign in with your GitHub account.
2. *File → Clone repository → GitHub.com* → choose `hkeremakts/FORGE-ee493` → pick a local folder → **Clone**.

**Option B – Terminal**
1. Install Git: https://git-scm.com/downloads (Windows: keep default options).
2. Tell Git who you are (once per computer):
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your-github-email@example.com"
   ```
3. Clone the repository into a folder you'll remember:
   ```bash
   git clone https://github.com/hkeremakts/FORGE-ee493.git
   cd FORGE-ee493
   ```
   The first push asks you to sign in to GitHub in the browser. Accept it.

### 1.3 Fill in your folder
Open **your own folder** (e.g. `GunesCeylan/`) and fill in `README.md`: your subsystem and related FR codes.
Then do your first push (Section 2). You now have a working setup.

---

## 2. Every work session

| Step | GitHub Desktop | Terminal |
|---|---|---|
| 1. Get latest changes | Click **Fetch origin**, then **Pull origin** | `git pull` |
| 2. Work | Edit files **only in your folder** | same |
| 3. Update log | Add a dated entry to your `LOG.md` (top of file) | same |
| 4. Select your changes | In the *Changes* list, tick **only** files in your folder | `git add YourFolder/` |
| 5. Commit | Summary: `[YourFolder] short description` → **Commit to main** | `git commit -m "[YourFolder] short description"` |
| 6. Upload | Click **Push origin** | `git push` |

**Push rejected?** Someone pushed before you. Pull first (step 1), then push again. Never force push.

---

## 3. Using your AI assistant

Everyone uses **one chat for this project**. Start that chat with the starter prompt in Section 4.
Pick the mode that matches your AI setup.

### Mode A – Your AI can access the repository
Use this if your AI is connected to GitHub, or works on your local files (Claude Code, Claude desktop with a linked folder, Cursor, VS Code + Copilot, etc.).

1. Point the AI to your local `FORGE-ee493` folder (or connect the GitHub repo).
2. Paste the starter prompt (Section 4) as the first message.
3. The AI reads RULEBOOK.md, your README and LOG itself, works in your folder, updates the log, and commits/pushes (or tells you to).
4. Check what it changed before pushing, at least at the start.

### Mode B – Your AI is NOT connected (ChatGPT/Claude/Gemini in a browser)
The AI can't see the files, so **you are the bridge**.

**Start of a session**
1. Pull the latest changes (Section 2, step 1).
2. In your project chat, paste the starter prompt (first time only), then paste these three files:
   - `RULEBOOK.md` (first time only, or when it changes)
   - your `README.md`
   - your `LOG.md` (the latest few entries are enough)

   Or simply attach them as files if your AI supports uploads.

**During the session**
- Work with the AI as usual. When it gives you code or files, save them **inside your folder** on your computer.

**End of a session**
1. Ask the AI:
   > *"Session is over. Give me the new LOG.md entry and the updated README.md, following the RULEBOOK format."*
2. Paste the new entry at the **top** of your `LOG.md` (below the title), and replace your `README.md` if it changed.
3. Commit and push (Section 2, steps 4–6).

---

## 4. Starter prompt

Copy this, replace the `<…>` parts, and send it as the first message of your project chat.

```
You are my assistant for the FORGE team's RAPTOR project (METU EE493/494).
I am <FULL NAME>, and my folder in the repository is /<FolderName>/.
My subsystem is <SUBSYSTEM NAME>.

Before doing anything:
1. Read RULEBOOK.md in the repository root and follow it strictly.
   (If you cannot access the repository, I will paste RULEBOOK.md, my README.md and my LOG.md here.)
2. Read my README.md and LOG.md to understand the current state of my work.

While working:
- Only create or change files inside /<FolderName>/.
- If something needs to change in /shared/ or in another member's folder, tell me instead of doing it.
- Do not commit large files (datasets, videos, model weights). Remind me to put them in the team Google Drive.
- Record every decision as: Decision / Alternatives considered / Reason.

At the end of every work session:
- Write a dated LOG.md entry in the RULEBOOK format, including all decisions.
- Give me the updated README.md if the current state changed.
- If you can access the repository: commit with "[<FolderName>] short description" and push.
  If you cannot: give me the files and the commit message so I can commit and push myself.
```

---

## 5. Common problems

| Problem | Fix |
|---|---|
| `Permission denied` / `403` when pushing | You haven't accepted the collaborator invite, or you're signed in with another GitHub account. |
| Push rejected (`fetch first` / `non-fast-forward`) | `git pull`, then `git push` again. |
| Pull says *merge conflict* | You edited a file someone else also edited (probably outside your folder). Don't guess, ask Kerem. |
| File too large / push takes forever | You added a dataset, video or model weight. Remove it from the folder, upload to Google Drive, put the link in your README. Ask Kerem if it was already committed. |
| I accidentally changed someone else's file | Before committing: in GitHub Desktop right-click → *Discard changes*; terminal: `git restore <file>`. |
| My AI edited files outside my folder | Discard those changes (row above) and remind the AI of the RULEBOOK. |

Questions → team group chat.
