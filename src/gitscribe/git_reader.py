"""
Read Git repository data from the .git directory.
Uses GitPython in local-only mode; no network or external APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError


@dataclass
class CommitInfo:
    """Single commit with metadata derived from Git."""

    sha: str
    short_sha: str
    author: str
    author_email: str
    authored_date: datetime
    committer: str
    committed_date: datetime
    message: str
    message_subject: str
    message_body: str
    parent_shas: list[str]
    tags: list[str] = field(default_factory=list)
    branches: list[str] = field(default_factory=list)


@dataclass
class TagInfo:
    """Tag with optional commit reference."""

    name: str
    sha: str | None
    is_annotated: bool
    tagger: str | None
    tag_date: datetime | None
    tag_message: str | None


@dataclass
class DiffStat:
    """Per-file change stats for a commit."""

    path: str
    insertions: int
    deletions: int
    is_binary: bool
    renamed_from: str | None = None


@dataclass
class FileHistoryEntry:
    """One point in a file's history (commit + path at that time)."""

    commit_sha: str
    path: str
    action: str  # 'A' add, 'M' modify, 'D' delete, 'R' rename
    previous_path: str | None = None


def _safe_decode(b: bytes | str) -> str:
    if isinstance(b, str):
        return b
    try:
        return b.decode("utf-8", errors="replace")
    except Exception:
        return str(b)


class GitReader:
    """Reads repository history and structure from .git only."""

    def __init__(self, repo_path: str | Path) -> None:
        path = Path(repo_path).resolve()
        if not (path / ".git").exists():
            raise InvalidGitRepositoryError(str(path))
        self.repo = Repo(path, odbt=type(Repo(path).odb))  # ensure no remote ops
        self.repo_path = path

    def get_commit_count(self) -> int:
        try:
            return self.repo.git.rev_list("--count", "HEAD")
        except GitCommandError:
            return 0

    def iter_commits(
        self,
        rev: str = "HEAD",
        max_count: int | None = None,
        skip: int = 0,
        first_parent: bool = True,
    ) -> Iterator[CommitInfo]:
        """Yield commits in reverse chronological order (newest first)."""
        try:
            kwargs: dict = {"rev": rev}
            if max_count is not None:
                kwargs["max_count"] = max_count
            if skip:
                kwargs["skip"] = skip
            if first_parent:
                kwargs["first_parent"] = True
            for c in self.repo.iter_commits(**kwargs):
                subject, _, body = (c.message or "").partition("\n")
                subject = subject.strip()
                body = body.strip()
                yield CommitInfo(
                    sha=c.hexsha,
                    short_sha=c.hexsha[:7],
                    author=_safe_decode(getattr(c.author, "name", "") or ""),
                    author_email=_safe_decode(getattr(c.author, "email", "") or ""),
                    authored_date=c.authored_datetime,
                    committer=_safe_decode(getattr(c.committer, "name", "") or ""),
                    committed_date=c.committed_datetime,
                    message=c.message or "",
                    message_subject=subject,
                    message_body=body,
                    parent_shas=[p.hexsha for p in c.parents],
                    tags=[],
                    branches=[],
                )
        except (GitCommandError, ValueError, TypeError):
            return

    def get_all_commits(self, first_parent: bool = True) -> list[CommitInfo]:
        """Return all commits on the default branch (newest first)."""
        commits = list(self.iter_commits(first_parent=first_parent))
        self._attach_refs(commits)
        return commits

    def _attach_refs(self, commits: list[CommitInfo]) -> None:
        """Attach tag and branch names to commits by SHA."""
        sha_to_commit = {c.sha: c for c in commits}
        for ref in self.repo.refs:
            try:
                sha = ref.commit.hexsha if hasattr(ref, "commit") else None
                if not sha:
                    continue
                name = ref.name
                if name.startswith("refs/tags/"):
                    tag_name = name.replace("refs/tags/", "")
                    if sha in sha_to_commit:
                        sha_to_commit[sha].tags.append(tag_name)
                elif name.startswith("refs/heads/"):
                    branch_name = name.replace("refs/heads/", "")
                    if sha in sha_to_commit:
                        sha_to_commit[sha].branches.append(branch_name)
            except (GitCommandError, ValueError, TypeError):
                continue

    def get_tags(self) -> list[TagInfo]:
        """Return all tags with commit SHA and optional annotation."""
        result: list[TagInfo] = []
        for tag_ref in self.repo.tags:
            try:
                tag = tag_ref.tag
                if tag is not None:
                    result.append(
                        TagInfo(
                            name=tag_ref.name,
                            sha=tag.commit.hexsha if hasattr(tag, "commit") else None,
                            is_annotated=True,
                            tagger=getattr(tag.tagger, "name", None) if hasattr(tag, "tagger") else None,
                            tag_date=getattr(tag, "tagged_date", None),
                            tag_message=getattr(tag, "message", None) or None,
                        )
                    )
                else:
                    result.append(
                        TagInfo(
                            name=tag_ref.name,
                            sha=tag_ref.commit.hexsha if hasattr(tag_ref, "commit") else None,
                            is_annotated=False,
                            tagger=None,
                            tag_date=None,
                            tag_message=None,
                        )
                    )
            except (GitCommandError, ValueError, TypeError, AttributeError):
                result.append(
                    TagInfo(
                        name=tag_ref.name,
                        sha=None,
                        is_annotated=False,
                        tagger=None,
                        tag_date=None,
                        tag_message=None,
                    )
                )
        return result

    def get_branches(self) -> list[tuple[str, str]]:
        """Return (branch_name, head_sha) for each local branch."""
        out: list[tuple[str, str]] = []
        for ref in self.repo.heads:
            try:
                out.append((ref.name, ref.commit.hexsha))
            except (GitCommandError, ValueError):
                continue
        return out

    def get_diff_stats(self, commit_sha: str, parent_sha: str | None = None) -> list[DiffStat]:
        """Return per-file diff stats for a commit using git show --numstat (accurate counts)."""
        try:
            import re
            output = self.repo.git.show(commit_sha, "--numstat", "--format=")
            result: list[DiffStat] = []
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                add_s, del_s, path = parts[0], parts[1], parts[2]
                insertions = int(add_s) if add_s != "-" else 0
                deletions = int(del_s) if del_s != "-" else 0
                result.append(
                    DiffStat(
                        path=path,
                        insertions=insertions,
                        deletions=deletions,
                        is_binary=add_s == "-" and del_s == "-",
                    )
                )
            return result
        except (GitCommandError, ValueError, TypeError):
            return []

    def get_file_history(self, path: str, rev: str = "HEAD") -> list[FileHistoryEntry]:
        """Return history of a file (commits that touched it) in chronological order."""
        try:
            log = self.repo.git.log(rev, "--follow", "--name-status", "--", path)
            entries: list[FileHistoryEntry] = []
            current_sha: str | None = None
            for line in log.splitlines():
                if not line:
                    continue
                if line.startswith("commit "):
                    current_sha = line.split()[1].strip()
                    continue
                if current_sha and line[0] in "AMDTRC" and "\t" in line:
                    action = line[0]
                    parts = line[1:].strip().split("\t")
                    p = parts[0].strip() if parts else ""
                    prev = parts[1].strip() if len(parts) > 1 else None
                    if action == "R" and prev:
                        entries.append(
                            FileHistoryEntry(
                                commit_sha=current_sha,
                                path=p,
                                action=action,
                                previous_path=prev,
                            )
                        )
                    else:
                        entries.append(
                            FileHistoryEntry(
                                commit_sha=current_sha,
                                path=p,
                                action=action,
                                previous_path=prev if action == "R" else None,
                            )
                        )
            return entries
        except (GitCommandError, ValueError, TypeError):
            return []

    def get_file_paths_at_rev(self, rev: str = "HEAD") -> list[str]:
        """Return all tracked file paths at a revision (tree walk)."""
        try:
            commit = self.repo.commit(rev)
            out: list[str] = []
            for item in commit.tree.traverse():
                if item.type == "blob":
                    out.append(item.path)
            return sorted(out)
        except (GitCommandError, ValueError, TypeError):
            return []

    def get_commit_message(self, sha: str) -> str:
        """Return full commit message for a SHA."""
        try:
            return self.repo.commit(sha).message or ""
        except (GitCommandError, ValueError, TypeError):
            return ""
