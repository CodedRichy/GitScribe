"""
Detect breaking changes from commit messages and heuristics.
Deterministic: only uses patterns in commit text and diff magnitude.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from gitscribe.git_reader import CommitInfo, GitReader, DiffStat


BREAKING_PATTERNS = [
    re.compile(r"\bBREAKING\s+CHANGE[S]?\b", re.IGNORECASE),
    re.compile(r"\bbreaking\s*:\s*", re.IGNORECASE),
    re.compile(r"^break(s|ing)?\s*[:\s]", re.IGNORECASE),
    re.compile(r"\[breaking\s*change\]", re.IGNORECASE),
    re.compile(r"BREAKING\s*-\s*", re.IGNORECASE),
    re.compile(r"incompatible\s+change", re.IGNORECASE),
    re.compile(r"api\s+breaking", re.IGNORECASE),
]

# Conventional commits
CONVENTIONAL_BREAKING = re.compile(r"^(\w+)(\([^)]*\))?!\s*:", re.IGNORECASE)


@dataclass
class BreakingChange:
    """A detected breaking change tied to a commit."""

    commit_sha: str
    short_sha: str
    subject: str
    evidence: str  # Which rule matched
    message_snippet: str


def detect_breaking_changes(
    reader: GitReader,
    commits: list[CommitInfo],
    *,
    large_deletion_threshold: int = 500,
) -> list[BreakingChange]:
    """
    Identify commits that likely represent breaking changes.
    Uses only: commit message patterns and large deletions (heuristic).
    """
    result: list[BreakingChange] = []
    seen_shas: set[str] = set()

    for c in commits:
        if c.sha in seen_shas:
            continue
        full_text = f"{c.message_subject}\n{c.message_body}"

        # 1) Explicit BREAKING in message
        for pat in BREAKING_PATTERNS:
            if pat.search(full_text):
                result.append(
                    BreakingChange(
                        commit_sha=c.sha,
                        short_sha=c.short_sha,
                        subject=c.message_subject,
                        evidence="message_breaking_keyword",
                        message_snippet=_truncate(full_text, 200),
                    )
                )
                seen_shas.add(c.sha)
                break
        if c.sha in seen_shas:
            continue

        # 2) Conventional commit with !
        if CONVENTIONAL_BREAKING.match(c.message_subject.strip()):
            result.append(
                BreakingChange(
                    commit_sha=c.sha,
                    short_sha=c.short_sha,
                    subject=c.message_subject,
                    evidence="conventional_breaking",
                    message_snippet=_truncate(full_text, 200),
                )
            )
            seen_shas.add(c.sha)
            continue

        # 3) Heuristic: very large net deletion (often API/module removal)
        try:
            stats = reader.get_diff_stats(c.sha)
            total_del = sum(s.deletions for s in stats)
            total_ins = sum(s.insertions for s in stats)
            if total_del >= large_deletion_threshold and total_del > total_ins * 2:
                result.append(
                    BreakingChange(
                        commit_sha=c.sha,
                        short_sha=c.short_sha,
                        subject=c.message_subject,
                        evidence="large_deletion_heuristic",
                        message_snippet=_truncate(full_text, 200),
                    )
                )
                seen_shas.add(c.sha)
        except Exception:
            pass

    return result


def _truncate(s: str, max_len: int) -> str:
    s = s.strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 3].rstrip() + "..."
