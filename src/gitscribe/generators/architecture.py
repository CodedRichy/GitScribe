"""
Generate ARCHITECTURE.md from module structure and evolution snapshots.
"""

from __future__ import annotations

from gitscribe.analyzers.architecture import (
    ArchitectureEvolution,
    ArchitectureSnapshot,
    ModuleNode,
)


def generate_architecture_md(
    evolution: ArchitectureEvolution,
    repo_name: str = "Repository",
) -> str:
    """
    Produce Markdown describing directory/module structure and how it evolved.
    """
    lines = [
        "# Architecture",
        "",
        f"Module and directory structure of **{repo_name}**, inferred from Git history. "
        "This document reflects how the codebase was organized at key points in time.",
        "",
        "---",
        "",
        "## Current structure (HEAD)",
        "",
    ]
    if evolution.snapshots:
        latest = evolution.snapshots[-1]
        lines.extend(_format_snapshot(latest))
    else:
        lines.append("No revision data available.")
        lines.append("")

    lines.append("## Evolution over time")
    lines.append("")
    lines.append("Snapshots at tagged or sampled revisions:")
    lines.append("")
    for snap in evolution.snapshots[:-1][-10:]:  # last 10 excluding current
        lines.append(f"### At {snap.rev_display} ({snap.date})")
        lines.append("")
        lines.append(f"- **Total files:** {snap.total_files}")
        lines.append(f"- **Top-level directories:** {', '.join(snap.top_level_dirs) or '(none)'}")
        lines.append("")
        for name in sorted(snap.modules.keys()):
            node = snap.modules[name]
            if "/" not in name:  # top-level only in summary
                lines.append(f"- `{name}/` — {node.file_count} files")
        lines.append("")

    if evolution.high_level_changes:
        lines.append("## Notable structural changes")
        lines.append("")
        for sha, _ct, desc in evolution.high_level_changes[:15]:
            lines.append(f"- {desc} (commit `{sha[:7]}`)")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Generated from Git tree and commit history. No external APIs used.*")
    lines.append("")
    return "\n".join(lines)


def _format_snapshot(snap: ArchitectureSnapshot) -> list[str]:
    out = [
        f"- **Total files:** {snap.total_files}",
        f"- **Top-level directories:** {', '.join(snap.top_level_dirs) or '(none)'}",
        "",
        "### Top-level modules",
        "",
    ]
    for name in sorted(snap.modules.keys()):
        node = snap.modules[name]
        if "/" in name:
            continue
        out.append(f"| `{name}/` | {node.file_count} files |")
    out.append("")
    return out
