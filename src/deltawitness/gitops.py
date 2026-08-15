"""Conservative Git operations used by the counterfactual matrix."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from fnmatch import fnmatchcase
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
from typing import Iterator, Sequence

from .config import PathPolicy
from .errors import GitError


@dataclass(frozen=True)
class ClassifiedChange:
    path: str
    status: str
    category: str


@dataclass(frozen=True)
class PathClassification:
    code: tuple[ClassifiedChange, ...]
    tests: tuple[ClassifiedChange, ...]
    documentation: tuple[ClassifiedChange, ...]

    @property
    def all(self) -> tuple[ClassifiedChange, ...]:
        return self.code + self.tests + self.documentation


def _git_environment() -> dict[str, str]:
    env: dict[str, str] = {}
    for name in ("PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TMPDIR", "TMP", "TEMP"):
        value = os.environ.get(name)
        if value is not None:
            env[name] = value
    env.setdefault("PATH", os.defpath)
    env.update(
        {
            "LC_ALL": "C",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "Never",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_LITERAL_PATHSPECS": "1",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_ATTR_NOSYSTEM": "1",
            "GIT_LFS_SKIP_SMUDGE": "1",
        }
    )
    return env


def _run_git(repo: Path, args: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=_git_environment(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and completed.returncode != 0:
        rendered = " ".join(["git", *args])
        raise GitError(f"Git command failed ({rendered}): {completed.stderr.strip()}")
    return completed


def _run_git_bytes(repo: Path, args: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=_git_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and completed.returncode != 0:
        rendered = " ".join(["git", *args])
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GitError(f"Git command failed ({rendered}): {stderr}")
    return completed


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    if not start.exists():
        raise GitError(f"Repository path does not exist: {start}")
    if start.is_file():
        start = start.parent
    completed = _run_git(start, ["rev-parse", "--show-toplevel"])
    return Path(completed.stdout.strip()).resolve()


def _validate_ref_argument(ref: str) -> None:
    if not ref or "\x00" in ref:
        raise GitError("Git ref must be a non-empty string without NUL bytes")


def resolve_ref(repo: Path, ref: str) -> str:
    _validate_ref_argument(ref)
    completed = _run_git(
        repo,
        ["rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"],
    )
    return completed.stdout.strip()


def resolve_tree(repo: Path, ref: str) -> str:
    _validate_ref_argument(ref)
    completed = _run_git(
        repo,
        ["rev-parse", "--verify", "--end-of-options", f"{ref}^{{tree}}"],
    )
    return completed.stdout.strip()


def ensure_clean(repo: Path) -> None:
    completed = _run_git(repo, ["status", "--porcelain=v1", "--untracked-files=normal"])
    if completed.stdout.strip():
        raise GitError("Repository must be clean before verification")


def ensure_ancestor(repo: Path, base_sha: str, head_sha: str) -> None:
    completed = _run_git(repo, ["merge-base", "--is-ancestor", base_sha, head_sha], check=False)
    if completed.returncode == 0:
        return
    if completed.returncode == 1:
        raise GitError("Base commit must be an ancestor of the candidate commit")
    raise GitError(f"Cannot determine commit ancestry: {completed.stderr.strip()}")


def _validate_changed_path(path: str) -> None:
    if not path or path.startswith("/") or "\x00" in path:
        raise GitError(f"Unsafe Git path in commit range: {path!r}")
    if "\\" in path:
        raise GitError(
            f"Backslashes in changed Git paths are not supported across platforms: {path!r}"
        )
    parts = PurePosixPath(path).parts
    if any(part in {".", ".."} or part.casefold() == ".git" for part in parts):
        raise GitError(f"Unsafe Git path in commit range: {path!r}")


def changed_paths(repo: Path, base_sha: str, head_sha: str) -> tuple[tuple[str, str], ...]:
    completed = _run_git_bytes(
        repo,
        ["diff", "--name-status", "-z", "--no-renames", base_sha, head_sha],
    )
    fields = completed.stdout.split(b"\0")
    if fields and fields[-1] == b"":
        fields.pop()
    if len(fields) % 2:
        raise GitError("Cannot parse NUL-delimited Git diff output")

    changes: list[tuple[str, str]] = []
    for index in range(0, len(fields), 2):
        status = fields[index].decode("ascii", errors="strict")
        path = fields[index + 1].decode("utf-8", errors="surrogateescape")
        _validate_changed_path(path)
        if status not in {"A", "M", "D", "T"}:
            raise GitError(f"Unsupported Git change status {status!r} for path {path!r}")
        changes.append((status, path))
    return tuple(changes)


def _matches(path: str, patterns: Sequence[str]) -> bool:
    return any(fnmatchcase(path, pattern) for pattern in patterns)


def classify_changes(
    changes: Sequence[tuple[str, str]],
    policy: PathPolicy,
) -> PathClassification:
    if not changes:
        raise GitError("No changed paths were found between base and candidate")

    buckets: dict[str, list[ClassifiedChange]] = {"code": [], "tests": [], "documentation": []}
    for status, path in changes:
        categories: list[str] = []
        if _matches(path, policy.code_globs):
            categories.append("code")
        if _matches(path, policy.test_globs):
            categories.append("tests")
        if _matches(path, policy.documentation_globs):
            categories.append("documentation")

        if not categories:
            raise GitError(
                f"Changed path is outside the declared boundary: {path!r}. "
                "Classify every changed path as code, tests, or documentation."
            )
        if len(categories) > 1:
            raise GitError(f"Changed path matches multiple categories {categories}: {path!r}")
        category = categories[0]
        buckets[category].append(ClassifiedChange(path=path, status=status, category=category))

    if not buckets["code"]:
        raise GitError("No changed code paths were found")
    if not buckets["tests"]:
        raise GitError("No changed test paths were found; this prototype requires a candidate witness")

    return PathClassification(
        code=tuple(buckets["code"]),
        tests=tuple(buckets["tests"]),
        documentation=tuple(buckets["documentation"]),
    )


def _path_exists_at_ref(repo: Path, ref: str, path: str) -> bool:
    completed = _run_git(repo, ["cat-file", "-e", f"{ref}:{path}"], check=False)
    return completed.returncode == 0


def _path_mode_at_ref(repo: Path, ref: str, path: str) -> str | None:
    completed = _run_git_bytes(repo, ["ls-tree", "-z", ref, "--", path])
    if not completed.stdout:
        return None
    record = completed.stdout.split(b"\0", maxsplit=1)[0]
    metadata, separator, _ = record.partition(b"\t")
    if not separator:
        raise GitError(f"Cannot parse Git tree entry for {path!r} at {ref}")
    fields = metadata.split()
    if len(fields) != 3:
        raise GitError(f"Cannot parse Git tree metadata for {path!r} at {ref}")
    return fields[0].decode("ascii")


def ensure_supported_entries(repo: Path, base_sha: str, head_sha: str, paths: Sequence[str]) -> None:
    for path in paths:
        for ref in (base_sha, head_sha):
            mode = _path_mode_at_ref(repo, ref, path)
            if mode == "160000":
                raise GitError(f"Changed Git submodule entries are not supported: {path!r}")


def overlay_paths(repo: Path, worktree: Path, source_ref: str, paths: Sequence[str]) -> None:
    for path in paths:
        target = worktree / path
        if _path_exists_at_ref(repo, source_ref, path):
            target.parent.mkdir(parents=True, exist_ok=True)
            completed = subprocess.run(
                ["git", "checkout", source_ref, "--", path],
                cwd=worktree,
                env=_git_environment(),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if completed.returncode != 0:
                raise GitError(f"Cannot overlay {path!r} from {source_ref}: {completed.stderr.strip()}")
        else:
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            elif target.exists() or target.is_symlink():
                target.unlink()
            completed = _run_git(
                worktree,
                ["rm", "--cached", "--ignore-unmatch", "--", path],
                check=False,
            )
            if completed.returncode not in {0, 1}:
                raise GitError(f"Cannot remove overlaid path {path!r}: {completed.stderr.strip()}")


def write_tree(worktree: Path) -> str:
    completed = _run_git(worktree, ["write-tree"])
    return completed.stdout.strip()


def create_synthetic_commit(
    repo: Path,
    tree_sha: str,
    parent_sha: str,
    *,
    state: str,
    base_sha: str,
    head_sha: str,
) -> str:
    env = _git_environment()
    env.update(
        {
            "GIT_AUTHOR_NAME": "DeltaWitness",
            "GIT_AUTHOR_EMAIL": "noreply@deltawitness.invalid",
            "GIT_AUTHOR_DATE": "1970-01-01T00:00:00Z",
            "GIT_COMMITTER_NAME": "DeltaWitness",
            "GIT_COMMITTER_EMAIL": "noreply@deltawitness.invalid",
            "GIT_COMMITTER_DATE": "1970-01-01T00:00:00Z",
        }
    )
    message = (
        f"DeltaWitness synthetic state: {state}\n\n"
        f"base: {base_sha}\n"
        f"head: {head_sha}\n"
    )
    completed = subprocess.run(
        ["git", "commit-tree", tree_sha, "-p", parent_sha],
        cwd=repo,
        env=env,
        input=message,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise GitError(f"Cannot create synthetic state commit {state!r}: {completed.stderr.strip()}")
    return completed.stdout.strip()


def restore_commit(worktree: Path, commit_sha: str) -> None:
    _run_git(worktree, ["reset", "--hard", commit_sha])
    _run_git(worktree, ["clean", "-ffdx"])


@contextmanager
def worktree(repo: Path, ref: str, prefix: str) -> Iterator[Path]:
    parent = Path(tempfile.mkdtemp(prefix="deltawitness-"))
    path = parent / prefix
    try:
        _run_git(repo, ["worktree", "add", "--detach", "--force", str(path), ref])
        yield path
    finally:
        _run_git(repo, ["worktree", "remove", "--force", str(path)], check=False)
        shutil.rmtree(parent, ignore_errors=True)
        _run_git(repo, ["worktree", "prune"], check=False)


def safe_path_label(path: Path, repo: Path) -> tuple[str, bool]:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix(), False
    except ValueError:
        return path.name, True


def git_metadata_path(repo: Path, relative_path: str) -> Path:
    if not relative_path or "\x00" in relative_path or Path(relative_path).is_absolute():
        raise GitError("Git metadata path must be a non-empty relative path")
    completed = _run_git(repo, ["rev-parse", "--git-path", relative_path])
    path = Path(completed.stdout.strip())
    return path.resolve() if path.is_absolute() else (repo / path).resolve()


def git_version() -> str:
    completed = subprocess.run(
        ["git", "--version"],
        env=_git_environment(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise GitError("Git is not available")
    return completed.stdout.strip()
