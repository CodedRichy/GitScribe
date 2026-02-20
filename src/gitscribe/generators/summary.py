"""
Generate optional summary report: high-churn files and unstable components.
"""

from __future__ import annotations

from gitscribe.analyzers.churn import ChurnReport


def generate_summary_md(
    churn: ChurnReport,
    repo_name: str = "Repository",
) -> str:
    """
    Produce Markdown summary of high-churn files and directory activity.
    """
    lines = [
        "# GitScribe summary report",
        "",
        f"High-churn and frequently changed areas in **{repo_name}**, "
        "computed from commit history (deterministic).",
        "",
        "---",
        "",
        "## High-churn files",
        "",
        "Files with the most commits and line changes over the project history.",
        "",
        "| Path | Commits | Insertions | Deletions | Total changes |",
        "|------|---------|------------|-----------|---------------|",
    ]
    for fc in churn.file_churns[:40]:
        lines.append(f"| `{fc.path}` | {fc.commit_count} | {fc.total_insertions} | {fc.total_deletions} | {fc.total_changes} |")
    lines.append("")
    lines.append("## Directory activity")
    lines.append("")
    lines.append("| Directory | Commits touching | Total line changes |")
    lines.append("|-----------|-------------------|---------------------|")
    for d, n_commits, n_lines in churn.dir_churns[:20]:
        lines.append(f"| `{d}/` | {n_commits} | {n_lines} |")
    lines.append("")

    if churn.unstable_paths:
        lines.append("## Unstable components")
        lines.append("")
        lines.append("Files changed often with relatively small diffs (possible refactors or volatile logic):")
        lines.append("")
        for p in churn.unstable_paths[:25]:
            lines.append(f"- `{p}`")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Generated from Git diff stats. Offline and deterministic.*")
    lines.append("")
    return "\n".join(lines)
