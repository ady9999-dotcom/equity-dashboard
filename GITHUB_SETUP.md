# Putting this project on GitHub — step by step

You've never used GitHub before, so this is written for a first-timer. Two paths are given. **Path A (GitHub Desktop) is the easiest** — no command line, no tokens. Path B is the command line, if you prefer it.

> **Make the repository PRIVATE.** This project is tied to your personal portfolio context. Your real positions are already excluded by `.gitignore`, but a **private** repo is the safe default. You can always make it public later.

---

## Before you start (both paths)

- Your personal data is already protected: `holdings_state.json`, `research_overlay.json`, and `research_archive/` are in `.gitignore` and will **not** be uploaded. (Verified.)
- A local git repository has already been initialised in this folder, and all the shareable files are staged. You just need to commit and publish.
- **OneDrive note:** this folder is inside OneDrive. Git works here, but if you ever see odd "file in use" errors during a commit, pause OneDrive sync for a few minutes (right-click the OneDrive cloud icon → Pause syncing).

---

## Path A — GitHub Desktop (recommended, no command line)

**1. Install GitHub Desktop**
- Go to **https://desktop.github.com** → Download for Windows → install.
- Open it → **Sign in** with your GitHub account.
- When asked, let it configure your name/email (this is your commit identity).

**2. Add this folder as a repository**
- Menu **File → Add local repository**.
- Click **Choose…** and select this folder (`…\Desktop\Claude`, or wherever you moved it).
- It should recognise it as a git repository (one was already initialised). If it says "this directory does not appear to be a Git repository", click the offered **"create a repository"** link instead.

**3. Make the first commit**
- The left panel lists all the files to be added (code + docs). Your personal data will **not** appear — that's correct.
- At the bottom-left, in the **Summary** box type: `Initial commit — v1.0.0`
- Click **Commit to main**.

**4. Publish to GitHub**
- Click **Publish repository** (top bar).
- Name it, e.g. **`equity-dashboard`**.
- **✅ Tick "Keep this code private"** — important.
- Click **Publish repository**.

Done. Your code is now on GitHub. Click **"View on GitHub"** to see it in your browser.

**5. Your everyday workflow from now on**
- Edit files as usual (or let Claude edit them).
- Open GitHub Desktop → it shows the changed files.
- Type a short summary (e.g. `v1.1.0: added NBFC CASA field`) → **Commit to main** → **Push origin**.

---

## Path B — Command line (git is already installed: v2.55)

**1. Set your identity (one time only)**
Open a terminal in this folder and run (use the email tied to your GitHub account):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**2. Make the first commit** (the folder is already `git init`-ed and files are staged):

```bash
git add -A
git commit -m "Initial commit — v1.0.0"
```

**3. Create an EMPTY repo on GitHub**
- Go to **https://github.com/new**.
- Repository name: `equity-dashboard`.
- **Select "Private".**
- **Do NOT** tick "Add a README", ".gitignore", or "license" — you already have them.
- Click **Create repository**. Copy the URL it shows (looks like `https://github.com/YOURNAME/equity-dashboard.git`).

**4. Connect and push**

```bash
git branch -M main
git remote add origin https://github.com/YOURNAME/equity-dashboard.git
git push -u origin main
```

**5. Authenticate on first push**
- A browser window opens → click **Authorize**. (Modern git uses this instead of a password.)
- If instead it asks for a username and password on the command line: the "password" is **NOT** your GitHub password — it's a **Personal Access Token**. Create one at **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token**, tick the **`repo`** scope, copy the token, and paste it as the password. (GitHub Desktop avoids this entirely — that's why Path A is easier.)

**Everyday workflow:**

```bash
git add -A
git commit -m "v1.1.0: <what changed>"
git push
```

---

## Versioning future enhancements

Before enhancing, read **CHANGELOG.md** (top entry = current version) and **docs/** so you build on what exists.

After a change:
1. Add a new dated section at the top of `CHANGELOG.md` describing what changed.
2. Commit with a matching message, e.g. `v1.1.0: bank CASA + PCR from investor deck`.
3. (Optional) tag the release so you can jump back to it:

```bash
git tag v1.1.0
git push --tags
```

To see history or go back to a previous version later:

```bash
git log --oneline          # list every commit
git checkout v1.0.0         # look at the v1.0.0 snapshot (read-only)
git checkout main           # return to the latest
```

---

## What NOT to commit (already handled by .gitignore)

- `holdings_state.json` — your real positions.
- `research_overlay.json`, `research_archive/` — research keyed to your holdings.
- Any `*.csv` / `*.xlsx` you drop in (broker exports, the audited-portfolio Excel).
- `__pycache__/`, `*.log`, `.claude/`.

If you ever *want* to include one of these (e.g. share a sanitised research overlay), remove its line from `.gitignore` first — but think twice about anything with your real financial data, and keep the repo private.
