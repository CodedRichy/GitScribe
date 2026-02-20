# GitScribe

**History-driven documentation generator** — analyzes a local Git repository by reading its `.git` directory and commit history to produce accurate, history-aware project documentation.

Documentation is derived **strictly from Git data** (commits, diffs, branches, tags, and file evolution). Git history is the primary source of truth; the tool does not infer intent from source code alone.

## Features

- **Reconstructs project evolution** over time from version control
- **Identifies major phases**: architectural shifts, breaking changes, refactors
- **Produces documentation** that reflects what actually happened, not only what the code looks like today
- **CLI-only**, **offline**, **deterministic** — no GitHub or external APIs; no LLM inventing facts

## Installation

Requires Python 3.9+ and a local Git repository.

```bash
# From the project root
pip install -e .

# Or install dependency only (run with: python -m gitscribe.cli)
pip install GitPython>=3.1.40
```

## Usage

```bash
# Analyze current directory (must be a Git repo)
gitscribe

# Specify repository path
gitscribe /path/to/repo

# Write output to a specific directory
gitscribe -o ./docs

# Also generate SUMMARY.md (high-churn files and unstable components)
gitscribe --with-summary

# Limit commits analyzed (default 5000)
gitscribe --max-commits 2000

# Quiet mode
gitscribe -q
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
