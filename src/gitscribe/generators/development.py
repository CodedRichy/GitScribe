"""
Generate DEVELOPMENT.md from the development timeline (features, refactors, decisions).
"""

from __future__ import annotations

from gitscribe.analyzers.timeline import TimelineEvent


def generate_development_md(
    events: list[TimelineEvent],
    repo_name: str = "Repository",
) -> str:
    """
    Produce Markdown timeline of major features, refactors, and technical decisions.
    """
    lines = [
        "# Development timeline",
        "",
        f"Chronological view of notable development events for **{repo_name}**, "
        "derived from commit history (messages and change scope).",
        "",
        "---",
        "",
    ]

    # Group by kind for a summary, then full timeline
    by_kind: dict[str, list[TimelineEvent]] = {}
    for e in events:
        by_kind.setdefault(e.kind, []).append(e)
    lines.append("## Summary by type")
    lines.append("")
    for kind in ("release", "feature", "refactor", "fix", "doc", "perf", "test", "chore", "other"):
        if kind not in by_kind:
            continue
        count = len(by_kind[kind])
        lines.append(f"- **{kind}**: {count} notable commit(s)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Timeline (newest first)")
    lines.append("")

    for e in events:
        date_str = e.date.strftime("%Y-%m-%d") if e.date else ""
        kind_badge = f"**[{e.kind}]**"
        lines.append(f"### {date_str} — {e.short_sha} {kind_badge}")
        lines.append("")
        lines.append(f"{e.subject}")
        lines.append("")
        if e.tags:
            lines.append(f"Tags: `{'`, `'.join(e.tags)}`")
            lines.append("")
        lines.append(f"Scope: {e.change_scope}")
        lines.append("")
        if e.body_snippet:
            lines.append("<details>")
            lines.append("<summary>Commit body</summary>")
            lines.append("")
            lines.append(e.body_snippet)
            lines.append("")
            lines.append("</details>")
            lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("*Generated from Git commits. Deterministic; no LLM inference.*")
    lines.append("")
    return "\n".join(lines)
