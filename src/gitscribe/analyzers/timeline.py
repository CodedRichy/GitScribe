"""
Build a development timeline: major features, refactors, technical decisions.
Derived from: commit messages, tags, diff size, and file renames/deletes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from gitscribe.git_reader import CommitInfo, GitReader, DiffStat


# Keywords that often indicate a notable change (feature/refactor/decision)
FEATURE_LIKE = ("feat", "feature", "add", "implement", "support", "introduce")
REFACTOR_LIKE = ("refactor", "rework", "restructure", "migrate", "move", "extract", "simplify")
FIX_LIKE = ("fix", "bugfix", "patch", "correct", "resolve")
DOC_LIKE = ("doc", "readme", "changelog", "documentation")
PERF_LIKE = ("perf", "performance", "optimize", "speed")
TEST_LIKE = ("test", "tests", "ci", "coverage")
CHORE_LIKE = ("chore", "deps", "dependencies", "bump", "style", "lint")


@dataclass
class TimelineEvent:
    """A single event on the development timeline."""

    commit_sha: str
    short_sha: str
    date: datetime
    kind: str  # "feature" | "refactor" | "fix" | "release" | "major_change" | "other"
    subject: str
    body_snippet: str
    tags: list[str]
    change_scope: str  # e.g. "15 files, +200 -50"


def build_development_timeline(
    reader: GitReader,
    commits: list[CommitInfo],
    tag_shas: set[str],
    *,
    max_events: int = 150,
    min_diff_lines: int = 30,
) -> list[TimelineEvent]:
    """
    Produce a chronological list of notable events (newest first in input = oldest first in output).
    Uses commit message keywords, tags (releases), and diff size.
    """
    events: list[TimelineEvent] = []

    for c in commits:
        subject_lower = (c.message_subject or "").lower()
        body_lower = (c.message_body or "").lower()
        combined = subject_lower + " " + body_lower

        kind = "other"
        if c.sha in tag_shas and c.tags:
            kind = "release"
        elif any(w in subject_lower for w in FEATURE_LIKE):
            kind = "feature"
        elif any(w in subject_lower for w in REFACTOR_LIKE):
            kind = "refactor"
        elif any(w in subject_lower for w in FIX_LIKE):
            kind = "fix"
        elif any(w in subject_lower for w in DOC_LIKE):
            kind = "doc"
        elif any(w in subject_lower for w in PERF_LIKE):
            kind = "perf"
        elif any(w in subject_lower for w in TEST_LIKE):
            kind = "test"
        elif any(w in subject_lower for w in CHORE_LIKE):
            kind = "chore"

        try:
            stats = reader.get_diff_stats(c.sha)
        except Exception:
            stats = []
        total_ins = sum(s.insertions for s in stats)
        total_del = sum(s.deletions for s in stats)
        num_files = len(stats)
        scope = f"{num_files} files, +{total_ins} -{total_del}"

        # Skip tiny commits unless release or clearly tagged
        if kind == "other" and (total_ins + total_del) < min_diff_lines and not c.tags:
            continue

        events.append(
            TimelineEvent(
                commit_sha=c.sha,
                short_sha=c.short_sha,
                date=c.authored_date,
                kind=kind,
                subject=c.message_subject or "(no subject)",
                body_snippet=(c.message_body or "")[:300].strip(),
                tags=list(c.tags),
                change_scope=scope,
            )
        )
        if len(events) >= max_events:
            break

    return events
