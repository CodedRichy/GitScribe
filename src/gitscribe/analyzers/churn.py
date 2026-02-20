"""
Compute file churn and identify unstable components.
Deterministic: only commit count and line deltas per file.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from gitscribe.git_reader import CommitInfo, GitReader, DiffStat


@dataclass
class FileChurn:
    """Churn metrics for a single file."""

    path: str
    commit_count: int
    total_insertions: int
    total_deletions: int
    total_changes: int


@dataclass
class ChurnReport:
    """High-churn files and directory-level summary."""

    file_churns: list[FileChurn]
    dir_churns: list[tuple[str, int, int]]  # (dir_path, total_commits, total_lines_changed)
    unstable_paths: list[str]  # Paths with very high churn relative to size (optional heuristic)


def compute_churn_report(
    reader: GitReader,
    commits: list[CommitInfo],
    *,
    top_n_files: int = 50,
    top_n_dirs: int = 20,
) -> ChurnReport:
    """
    Aggregate per-file and per-directory change counts over the commit history.
    """
    path_commits: dict[str, set[str]] = defaultdict(set)
    path_ins: dict[str, int] = defaultdict(int)
    path_del: dict[str, int] = defaultdict(int)

    for c in commits:
        try:
            stats = reader.get_diff_stats(c.sha)
        except Exception:
            continue
        for s in stats:
            path_commits[s.path].add(c.sha)
            path_ins[s.path] += s.insertions
            path_del[s.path] += s.deletions

    file_churns = [
        FileChurn(
            path=p,
            commit_count=len(path_commits[p]),
            total_insertions=path_ins[p],
            total_deletions=path_del[p],
            total_changes=path_ins[p] + path_del[p],
        )
        for p in path_commits
    ]
    file_churns.sort(key=lambda x: x.commit_count + (x.total_changes // 100), reverse=True)
    file_churns = file_churns[: top_n_files * 2]  # keep more then filter by total_changes too
    file_churns.sort(key=lambda x: (x.total_changes, x.commit_count), reverse=True)
    file_churns = file_churns[:top_n_files]

    # Directory-level: sum by directory from full path aggregates
    dir_commits = defaultdict(set)
    dir_lines = defaultdict(int)
    for p, commits_set in path_commits.items():
        d = _dir_of(p)
        if d:
            dir_commits[d].update(commits_set)
            dir_lines[d] += path_ins[p] + path_del[p]

    dir_churns = [
        (d, len(dir_commits[d]), dir_lines[d])
        for d in sorted(dir_commits.keys(), key=lambda x: (-dir_lines[x], -len(dir_commits[x])))
    ][:top_n_dirs]

    # Unstable: high commit count but not huge lines (churned often, refactored)
    unstable = [
        fc.path for fc in file_churns
        if fc.commit_count >= 10 and fc.total_changes < 500
    ][:30]

    return ChurnReport(
        file_churns=file_churns,
        dir_churns=dir_churns,
        unstable_paths=unstable,
    )


def _dir_of(path: str) -> str:
    p = path.replace("\\", "/")
    if "/" in p:
        return p.rsplit("/", 1)[0]
    return ""
