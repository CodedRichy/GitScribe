#!/usr/bin/env python3
"""
Run GitScribe without installing the package.
From the repo root:  python run.py [repo_path] [options]
Requires:  pip install GitPython
"""
import sys
from pathlib import Path

# Run from repo root so "gitscribe" can be imported from src
_repo_root = Path(__file__).resolve().parent
if str(_repo_root / "src") not in sys.path:
    sys.path.insert(0, str(_repo_root / "src"))

def main():
    try:
        from git.exc import InvalidGitRepositoryError  # noqa: F401
    except ImportError:
        print("GitScribe needs GitPython. Install it with:", file=sys.stderr)
        print("  pip install GitPython", file=sys.stderr)
        return 1
    from gitscribe.cli import main as cli_main
    return cli_main()

if __name__ == "__main__":
    sys.exit(main())
