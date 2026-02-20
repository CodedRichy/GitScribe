# GitScribe

**History-driven documentation generator** — analyzes a local Git repository by reading its `.git` directory and commit history to produce accurate, history-aware project documentation.

---

## How to use this (simple)

1. **You need:** Python 3.9+ and a folder that is a Git repo (it has a `.git` folder).

2. **One-time setup:** Open a terminal in the GitScribe project folder and run:
   ```bash
   pip install GitPython
   ```

3. **Generate docs:**
   - **This repo:** Open a terminal in the GitScribe folder and run:
     ```bash
     python run.py
     ```
   - **Another repo:** Run the same from anywhere, and give the path:
     ```bash
     python run.py C:\path\to\your\project
     ```

4. **What you get:** In the repo you pointed at (or the current folder), GitScribe creates three files:
   - **CHANGELOG.md** — What changed, by version and commit
   - **ARCHITECTURE.md** — How the project’s folders/files evolved
   - **DEVELOPMENT.md** — Timeline of features, refactors, fixes

   To also get **SUMMARY.md** (busiest files and unstable areas), run:
   ```bash
   python run.py --with-summary
   ```

That’s it. No account, no internet, no install of GitScribe itself — just `pip install GitPython` and `python run.py`.

---

## Quick start (other ways)

**Easiest (no install):** from the GitScribe repo folder:

```bash
pip install GitPython
python run.py
```

This analyzes the current directory (must be a Git repo) and writes `CHANGELOG.md`, `ARCHITECTURE.md`, and `DEVELOPMENT.md` there.

**One-command setup (PowerShell):** creates a venv and runs GitScribe:

```powershell
.\run.ps1
.\run.ps1 --with-summary
.\run.ps1 C:\path\to\other\repo
```

**Analyze another repo:**

```bash
python run.py C:\path\to\repo
python run.py C:\path\to\repo --with-summary -o C:\path\to\docs
```

## Features

- **Reconstructs project evolution** over time from version control
- **Identifies major phases**: architectural shifts, breaking changes, refactors
- **Produces documentation** that reflects what actually happened, not only what the code looks like today
- **CLI-only**, **offline**, **deterministic** — no GitHub or external APIs; no LLM inventing facts

## Installation (optional)

If you prefer to install the package (Python 3.9+):

```bash
pip install -e .
gitscribe
gitscribe /path/to/repo --with-summary
```

## Usage

```bash
# Analyze current directory (must be a Git repo)
python run.py
# or:  gitscribe

# Another repo
python run.py /path/to/repo
# or:  gitscribe /path/to/repo

# Write output to a specific directory
python run.py -o ./docs
# or:  gitscribe -o ./docs

# Include SUMMARY.md (high-churn and unstable components)
python run.py --with-summary
# or:  gitscribe --with-summary

# Limit commits (default 5000), quiet mode
python run.py --max-commits 2000 -q
```

## Outputs (Markdown)

| File | Description |
|------|-------------|
| **CHANGELOG.md** | Generated from tags, commit history, and detected breaking changes |
| **ARCHITECTURE.md** | Inferred module/directory structure and how it evolved over time |
| **DEVELOPMENT.md** | Timeline of major features, refactors, and technical decisions |
| **SUMMARY.md** | Optional; high-churn files and unstable components (use `--with-summary`) |

All files are written to the repository root (or `--output-dir`). They are suitable for real-world projects and emphasize **correctness** and **traceability** (commit SHAs, scopes, and dates).

## How it works

1. **Git reader** — Reads only the local `.git` directory (no network). Uses [GitPython](https://github.com/gitpython-developers/GitPython) to walk commits, tags, branches, and diffs.
2. **Analyzers** (deterministic):
   - **Breaking changes**: Message patterns (e.g. `BREAKING CHANGE`, `feat!:`), plus heuristics (e.g. very large deletions).
   - **Architecture**: File tree at key revisions (tags + sampled commits); top-level modules and notable structural changes.
   - **Timeline**: Event types (feature, refactor, fix, release, etc.) from commit message keywords and diff scope.
   - **Churn**: Per-file and per-directory commit counts and line deltas.
3. **Generators** — Turn analysis results into Markdown only; no LLM is used to invent content.

## Constraints

- **CLI only** — no graphical UI
- **Works offline** — no GitHub or other remote APIs
- **Deterministic** — LLMs may be used only to phrase findings, not to invent facts (this implementation uses no LLM)

## License

Copyright (c) 2025 Rishi Praseeth Krishnan. All rights reserved.

This repository and its source code are made visible for viewing and reference only. No license is granted to use, copy, modify, distribute, or create derivative works from this software. You may not use this code in your own projects, products, or services without express written permission from the copyright holder. Viewing the code (e.g., on GitHub) does not constitute permission to use it.
