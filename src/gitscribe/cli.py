"""
GitScribe CLI: analyze a Git repository and generate history-driven documentation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from git.exc import InvalidGitRepositoryError

from gitscribe import __version__
from gitscribe.git_reader import GitReader
from gitscribe.analyzers import (
    detect_breaking_changes,
    analyze_architecture_evolution,
    build_development_timeline,
    compute_churn_report,
)
from gitscribe.generators import (
    generate_changelog_md,
    generate_architecture_md,
    generate_development_md,
    generate_summary_md,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GitScribe — History-driven documentation from Git repository analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Outputs (Markdown, written to the repository or --output-dir):
  CHANGELOG.md    From tags, commit history, and detected breaking changes
  ARCHITECTURE.md Module structure and how it evolved over time
  DEVELOPMENT.md  Timeline of major features, refactors, and decisions
  SUMMARY.md      (optional) High-churn files and unstable components
        """,
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to the local Git repository (default: current directory)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default=None,
        help="Directory to write Markdown files (default: repository root)",
    )
    parser.add_argument(
        "--with-summary",
        action="store_true",
        help="Also generate SUMMARY.md (high-churn and unstable components)",
    )
    parser.add_argument(
        "--max-commits",
        type=int,
        default=5000,
        help="Maximum commits to analyze (default: 5000)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress messages",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else repo_path

    try:
        reader = GitReader(repo_path)
    except InvalidGitRepositoryError:
        print("fatal: not a Git repository (or .git not found)", file=sys.stderr)
        return 1

    if not args.quiet:
        print("GitScribe: analyzing Git history...", flush=True)

    commits = reader.get_all_commits()
    if args.max_commits and len(commits) > args.max_commits:
        commits = commits[: args.max_commits]
    if not args.quiet:
        print(f"  Commits analyzed: {len(commits)}", flush=True)

    tags = reader.get_tags()
    tags_by_sha: dict[str, list[str]] = {}
    tag_shas: set[str] = set()
    for t in tags:
        if t.sha:
            tags_by_sha.setdefault(t.sha, []).append(t.name)
            tag_shas.add(t.sha)

    repo_name = repo_path.name or "Repository"

    # Analyses (deterministic)
    breaking = detect_breaking_changes(reader, commits)
    evolution = analyze_architecture_evolution(reader, commits, tag_shas)
    timeline = build_development_timeline(reader, commits, tag_shas)
    churn = compute_churn_report(reader, commits)

    # Generators
    changelog_md = generate_changelog_md(commits, tags_by_sha, breaking, repo_name)
    architecture_md = generate_architecture_md(evolution, repo_name)
    development_md = generate_development_md(timeline, repo_name)
    summary_md = generate_summary_md(churn, repo_name)

    # Write files
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "CHANGELOG.md").write_text(changelog_md, encoding="utf-8")
    (output_dir / "ARCHITECTURE.md").write_text(architecture_md, encoding="utf-8")
    (output_dir / "DEVELOPMENT.md").write_text(development_md, encoding="utf-8")
    if args.with_summary:
        (output_dir / "SUMMARY.md").write_text(summary_md, encoding="utf-8")

    if not args.quiet:
        print(f"  Wrote: {output_dir / 'CHANGELOG.md'}")
        print(f"  Wrote: {output_dir / 'ARCHITECTURE.md'}")
        print(f"  Wrote: {output_dir / 'DEVELOPMENT.md'}")
        if args.with_summary:
            print(f"  Wrote: {output_dir / 'SUMMARY.md'}")
        print("Done.", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
