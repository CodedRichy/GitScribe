# GitScribe summary report

High-churn and frequently changed areas in **GitScribe**, computed from commit history (deterministic).

---

## High-churn files

Files with the most commits and line changes over the project history.

| Path | Commits | Insertions | Deletions | Total changes |
|------|---------|------------|-----------|---------------|
| `src/gitscribe/git_reader.py` | 1 | 293 | 0 | 293 |
| `src/gitscribe/generators/changelog.py` | 2 | 168 | 43 | 211 |
| `src/gitscribe/analyzers/architecture.py` | 1 | 141 | 0 | 141 |
| `src/gitscribe/cli.py` | 1 | 139 | 0 | 139 |
| `src/gitscribe/analyzers/breaking.py` | 1 | 114 | 0 | 114 |
| `src/gitscribe/analyzers/churn.py` | 1 | 104 | 0 | 104 |
| `src/gitscribe/analyzers/timeline.py` | 1 | 103 | 0 | 103 |
| `README.md` | 3 | 81 | 2 | 83 |
| `src/gitscribe/generators/architecture.py` | 1 | 83 | 0 | 83 |
| `src/gitscribe/generators/development.py` | 2 | 71 | 2 | 73 |
| `src/gitscribe/generators/summary.py` | 1 | 56 | 0 | 56 |
| `pyproject.toml` | 2 | 47 | 3 | 50 |
| `src/gitscribe.egg-info/PKG-INFO` | 1 | 25 | 0 | 25 |
| `src/gitscribe.egg-info/SOURCES.txt` | 1 | 21 | 0 | 21 |
| `src/gitscribe/analyzers/__init__.py` | 1 | 13 | 0 | 13 |
| `src/gitscribe/generators/__init__.py` | 1 | 13 | 0 | 13 |
| `LICENSE` | 1 | 7 | 0 | 7 |
| `src/gitscribe.egg-info/requires.txt` | 1 | 5 | 0 | 5 |
| `src/gitscribe/__init__.py` | 1 | 3 | 0 | 3 |
| `requirements.txt` | 1 | 2 | 0 | 2 |
| `src/gitscribe.egg-info/entry_points.txt` | 1 | 2 | 0 | 2 |
| `src/gitscribe.egg-info/dependency_links.txt` | 1 | 1 | 0 | 1 |
| `src/gitscribe.egg-info/top_level.txt` | 1 | 1 | 0 | 1 |
| `src/gitscribe/__pycache__/__init__.cpython-311.pyc` | 1 | 0 | 0 | 0 |
| `src/gitscribe/__pycache__/cli.cpython-311.pyc` | 1 | 0 | 0 | 0 |

## Directory activity

| Directory | Commits touching | Total line changes |
|-----------|-------------------|---------------------|
| `src/gitscribe/analyzers/` | 1 | 475 |
| `src/gitscribe/generators/` | 2 | 436 |
| `src/gitscribe/` | 2 | 435 |
| `src/gitscribe.egg-info/` | 1 | 55 |
| `src/gitscribe/__pycache__/` | 1 | 0 |

---

*Generated from Git diff stats. Offline and deterministic.*
