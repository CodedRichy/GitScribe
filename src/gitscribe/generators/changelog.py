"""
Generate CHANGELOG.md from tags, commit history, and detected breaking changes.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from gitscribe.git_reader import CommitInfo
from gitscribe.analyzers.breaking import BreakingChange


def generate_changelog_md(
    commits: list[CommitInfo],
    tags_by_sha: dict[str, list[str]],
    breaking: list[BreakingChange],
    repo_name: str = "Repository",
) -> str:
    """
    Produce Markdown changelog: sections by version (from tags), commits grouped,
    with a dedicated breaking changes section where applicable.
    """
    lines = [
        "# Changelog",
        "",
        f"All notable changes to **{repo_name}** are documented here. "
        "Generated from Git history (tags and commits).",
        "",
        "---",
        "",
    ]

    sha_to_commit = {c.sha: c for c in commits}
    tagged_shas = set(tags_by_sha.keys())
    ordered_tag_shas = [c.sha for c in commits if c.sha in tagged_shas]
    breaking_by_sha = {b.commit_sha: b for b in breaking}

    # Unreleased first
    if not ordered_tag_shas:
        unreleased = commits
    else:
        latest_tag_sha = ordered_tag_shas[0]
        idx = next((i for i, c in enumerate(commits) if c.sha == latest_tag_sha), 0)
        unreleased = commits[:idx] if idx else commits
    unreleased_breaking = [b for b in breaking if b.commit_sha in {c.sha for c in unreleased}]
    lines.append("## [Unreleased]")
    lines.append("")
    if unreleased_breaking:
        lines.append("### Breaking changes")
        lines.append("")
        for b in unreleased_breaking:
            lines.append(f"- **{b.subject}** (`{b.short_sha}`)")
            if b.message_snippet:
                lines.append(f"  - {_escape_md(b.message_snippet[:200])}")
            lines.append("")
        lines.append("### Other changes")
        lines.append("")
    for c in unreleased:
        if c.sha in breaking_by_sha:
            continue
        subj = c.message_subject or "(no subject)"
        lines.append(f"- {_escape_md(subj)} (`{c.short_sha}`)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Tagged releases (newest first in document)
    rev_list = list(reversed(ordered_tag_shas))  # oldest ... newest
    rev_newest_first = list(reversed(rev_list))
    if rev_newest_first:
        for i, tag_sha in enumerate(rev_newest_first):
            tag_names = tags_by_sha.get(tag_sha, [])
            version = tag_names[0] if tag_names else tag_sha[:7]
            next_tag_sha = rev_newest_first[i + 1] if i + 1 < len(rev_newest_first) else None  # older tag
            commit = sha_to_commit.get(tag_sha)
            date_str = commit.authored_date.strftime("%Y-%m-%d") if commit and commit.authored_date else ""
            lines.append(f"## [{version}] — {date_str}")
            lines.append("")
            section_commits = _commits_between(commits, tag_sha, next_tag_sha)
            section_breaking = [breaking_by_sha[c.sha] for c in section_commits if c.sha in breaking_by_sha]
            if section_breaking:
                lines.append("### Breaking changes")
                lines.append("")
                for b in section_breaking:
                    lines.append(f"- **{b.subject}** (`{b.short_sha}`)")
                    if b.message_snippet:
                        lines.append(f"  - {_escape_md(b.message_snippet[:200])}")
                    lines.append("")
                lines.append("### Other changes")
                lines.append("")
            for c in section_commits:
                if c.sha in breaking_by_sha:
                    continue
                subj = c.message_subject or "(no subject)"
                lines.append(f"- {_escape_md(subj)} (`{c.short_sha}`)")
            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def _commits_between(
    commits: list[CommitInfo],
    from_sha_excl: str | None,
    to_sha_incl: str | None,
) -> list[CommitInfo]:
    """Commits strictly after from_sha_excl (newer) until to_sha_incl (older). List is newest-first."""
    in_range = []
    started = from_sha_excl is None
    for c in commits:
        if to_sha_incl and c.sha == to_sha_incl:
            break
        if from_sha_excl and c.sha == from_sha_excl:
            started = True
            continue
        if started:
            in_range.append(c)
    return in_range


def _escape_md(s: str) -> str:
    # Avoid breaking list items and bold
    return s.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]") if s else ""
