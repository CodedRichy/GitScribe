# GitScribe

**History-driven documentation generator** — analyzes a local Git repository by reading its `.git` directory and commit history to produce accurate, history-aware project documentation.

Documentation is derived **strictly from Git data** (commits, diffs, branches, tags, and file evolution). Git history is the primary source of truth; the tool does not infer intent from source code alone.

## Quick start

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
