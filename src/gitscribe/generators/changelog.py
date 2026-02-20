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

    # Group commits by tag: from newest tag backward, assign commits to the tag that follows them
    sha_to_commit = {c.sha: c for c in commits}
    tagged_shas = set(tags_by_sha.keys())
    ordered_tag_shas = [c.sha for c in commits if c.sha in tagged_shas]
    breaking_by_sha = {b.commit_sha: b for b in breaking}

    # Sections: each tagged release gets a section; then "Unreleased" for commits after latest tag
    if ordered_tag_shas:
        # Newest tag first
        for i, tag_sha in enumerate(reversed(ordered_tag_shas)):
            tag_names = tags_by_sha.get(tag_sha, [])
            version = tag_names[0] if tag_names else tag_sha[:7]
            next_tag_sha = ordered_tag_shas[-(i + 2)] if i + 2 <= len(ordered_tag_shas) else None
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

    # Unreleased (commits after latest tag or all if no tags)
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

    return "\n".join(lines)


def _commits_between(
    commits: list[CommitInfo],
    after_sha: str,
    before_sha: str | None,
) -> list[CommitInfo]:
    """Commits after after_sha and before before_sha (exclusive), in order they appear in commits."""
    in_range = []
    found_after = False
    for c in commits:
        if c.sha == after_sha:
            found_after = True
            continue
        if found_after:
            if before_sha and c.sha == before_sha:
                break
            in_range.append(c)
    return in_range


def _escape_md(s: str) -> str:
    # Avoid breaking list items and bold
    return s.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]") if s else ""
