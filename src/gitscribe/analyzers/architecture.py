"""
Infer module/directory structure and how it evolved over time.
Derived only from: file paths at revisions and commit history (adds/renames/deletes).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from gitscribe.git_reader import CommitInfo, GitReader


@dataclass
class ModuleNode:
    """A directory or logical module (top-level path segment)."""

    path: str  # e.g. "src" or "src/foo"
    file_count: int
    first_seen_commit: str | None
    last_modified_commit: str | None
    child_paths: list[str] = field(default_factory=list)


@dataclass
class ArchitectureSnapshot:
    """Structure at a point in time (e.g. at a tag)."""

    rev: str
    rev_display: str  # tag name or short sha
    date: str
    top_level_dirs: list[str]
    modules: dict[str, ModuleNode]
    total_files: int


@dataclass
class ArchitectureEvolution:
    """Evolution of project structure over time."""

    snapshots: list[ArchitectureSnapshot]
    file_lifetime: dict[str, list[tuple[str, str]]]  # path -> [(commit, action), ...]
    high_level_changes: list[tuple[str, str, str]]  # (commit_sha, change_type, description)


def _top_level(path: str) -> str:
    p = path.replace("\\", "/")
    if "/" in p:
        return p.split("/")[0]
    return p


def _dir_path(path: str) -> str:
    p = path.replace("\\", "/")
    if "/" in p:
        return p.rsplit("/", 1)[0]
    return ""


def analyze_architecture_evolution(
    reader: GitReader,
    commits: list[CommitInfo],
    tag_shas: set[str],
    *,
    sample_revs: int = 20,
) -> ArchitectureEvolution:
    """
    Build snapshots of directory/module structure at key revisions (tags + sampled).
    Track file additions/renames/deletions for evolution narrative.
    """
    commits_by_sha = {c.sha: i for i, c in enumerate(commits)}
    # Key revisions: tagged commits + evenly sampled commits
    key_revs: list[tuple[str, str, str]] = []  # (sha, display, date)
    for c in commits:
        date = c.authored_date.strftime("%Y-%m-%d") if c.authored_date else ""
        if c.sha in tag_shas and c.tags:
            key_revs.append((c.sha, c.tags[0], date))
    # Add sampled commits if we have many
    step = max(1, len(commits) // max(1, sample_revs))
    for i in range(0, len(commits), step):
        c = commits[i]
        if not any(r[0] == c.sha for r in key_revs):
            key_revs.append((c.sha, c.short_sha, c.authored_date.strftime("%Y-%m-%d") if c.authored_date else ""))
    key_revs.sort(key=lambda x: commits_by_sha.get(x[0], 0))

    snapshots: list[ArchitectureSnapshot] = []
    for sha, display, date in key_revs:
        paths = reader.get_file_paths_at_rev(sha)
        top_level = sorted(set(_top_level(p) for p in paths))
        modules: dict[str, ModuleNode] = {}
        for top in top_level:
            files_in = [p for p in paths if _top_level(p) == top]
            modules[top] = ModuleNode(
                path=top,
                file_count=len(files_in),
                first_seen_commit=None,
                last_modified_commit=sha,
                child_paths=[],
            )
        snapshots.append(
            ArchitectureSnapshot(
                rev=sha,
                rev_display=display,
                date=date,
                top_level_dirs=top_level,
                modules=modules,
                total_files=len(paths),
            )
        )

    # File lifetime: which commits added/renamed/deleted key files (sample)
    file_lifetime: dict[str, list[tuple[str, str]]] = defaultdict(list)
    high_level_changes: list[tuple[str, str, str]] = []
    seen_commits_for_change: set[str] = set()
    for c in commits:
        try:
            stats = reader.get_diff_stats(c.sha)
        except Exception:
            continue
        added = [s.path for s in stats if s.insertions and not s.deletions and not s.renamed_from]
        deleted = [s.path for s in stats if s.deletions and not s.insertions]
        renamed = [(s.renamed_from, s.path) for s in stats if getattr(s, "renamed_from", None)]
        for path in added[:30]:  # cap to avoid huge dict
            file_lifetime[path].append((c.sha, "A"))
        for path in deleted[:30]:
            file_lifetime[path].append((c.sha, "D"))
        for a, b in renamed[:20]:
            if a:
                file_lifetime[a].append((c.sha, "R->" + b))

        # High-level: new top-level dir or big rename
        for path in added:
            top = _top_level(path)
            if top and top not in (snapshots[0].top_level_dirs if snapshots else []) and c.sha not in seen_commits_for_change:
                high_level_changes.append((c.sha, "new_top_level", f"Top-level directory '{top}' appears"))
                seen_commits_for_change.add(c.sha)

    return ArchitectureEvolution(
        snapshots=snapshots,
        file_lifetime=dict(file_lifetime),
        high_level_changes=high_level_changes,
    )
