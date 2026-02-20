# GitScribe

Generates **CHANGELOG.md**, **ARCHITECTURE.md**, and **DEVELOPMENT.md** from a repo’s Git history. No GitHub, no API — it only reads the local `.git` folder.

---

## What you need

- **Python 3.9+**
- A **Git repo** (the folder you want docs for must have a `.git` inside it)

---

## One-time setup

Install the only dependency (do this once):

```bash
pip install GitPython
```

---

## How to run it

**Option A — You’re in the GitScribe folder**

```bash
python run.py
```
Analyzes the current folder (must be a Git repo).

**Option B — You’re in the project you want docs for (e.g. GitPulse)**

```bash
python ..\GitScribe\run.py .
```
The `.` means “this folder.” Use the path to GitScribe if it’s not one level up, e.g.:

```bash
python C:\Users\rishi\Documents\GitHub\GitScribe\run.py .
```

**Option C — You’re in GitScribe and want to analyze another repo**

```bash
python run.py C:\path\to\other\project
```

---

## Where the files go

GitScribe writes all Markdown files into a **`docs`** folder inside the repo it analyzed. If the repo is `C:\GitPulse`, the files go in `C:\GitPulse\docs\`.

| File | What it is |
|------|------------|
| **CHANGELOG.md** | Changes by version/commit, plus breaking changes |
| **ARCHITECTURE.md** | How folders and structure changed over time |
| **DEVELOPMENT.md** | Timeline of features, refactors, fixes |

Add **SUMMARY.md** (busiest files, unstable areas) by running with:

```bash
python run.py . --with-summary
```
(or `python run.py C:\path\to\repo --with-summary`)

---

## Other options

| Option | Meaning |
|--------|--------|
| `--with-summary` | Also create SUMMARY.md |
| `-o FOLDER` | Write files into `FOLDER` instead of `docs` |
| `--max-commits 2000` | Limit how many commits to scan (default 5000) |
| `-q` | Less output while running |

Example (custom output folder):

```bash
python ..\GitScribe\run.py . --with-summary -o .\my-docs
```

---

## License

Copyright (c) 2025 Rishi Praseeth Krishnan. All rights reserved.

This repository and its source code are made visible for viewing and reference only. No license is granted to use, copy, modify, distribute, or create derivative works from this software. You may not use this code in your own projects, products, or services without express written permission from the copyright holder. Viewing the code (e.g., on GitHub) does not constitute permission to use it.
