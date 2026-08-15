#!/usr/bin/env python3
"""Reject common secret, private-path, and build-artifact leaks."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

_FORBIDDEN_PATH_PARTS = (
    ".deltawitness/",
    "__pycache__/",
    ".pytest_cache/",
    ".venv/",
)
_FORBIDDEN_SUFFIXES = (".pyc", ".pyo", ".pem", ".p12", ".pfx")
_FORBIDDEN_FILENAMES = {".env", ".env.local", ".DS_Store", "id_rsa", "id_ed25519"}
_MAX_TEXT_FILE_BYTES = 1_000_000


def _patterns() -> tuple[tuple[str, re.Pattern[str]], ...]:
    private_key = "-----BEGIN " + r"(?:RSA |EC |OPENSSH )?" + "PRIVATE KEY-----"
    return (
        ("private key", re.compile(private_key)),
        ("GitHub fine-grained token", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
        ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),
        ("OpenAI-style API key", re.compile(r"sk-[A-Za-z0-9_-]{32,}")),
        ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
        ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}")),
        ("absolute POSIX home path", re.compile(r"/home/[A-Za-z0-9._-]+/")),
        ("absolute Windows user path", re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\\\r\n]+\\\\")),
    )


def _tracked_files(root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace").strip())
    return [item.decode("utf-8", errors="surrogateescape") for item in completed.stdout.split(b"\0") if item]


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    patterns = _patterns()
    for relative in _tracked_files(root):
        normalized = relative.replace("\\", "/")
        path = root / relative
        if any(part in normalized for part in _FORBIDDEN_PATH_PARTS):
            errors.append(f"forbidden generated or private path: {relative!r}")
            continue
        if path.name in _FORBIDDEN_FILENAMES or path.suffix.lower() in _FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden sensitive or generated file: {relative!r}")
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            errors.append(f"cannot read tracked file {relative!r}: {exc}")
            continue
        if len(data) > _MAX_TEXT_FILE_BYTES:
            errors.append(f"tracked file exceeds {_MAX_TEXT_FILE_BYTES} bytes: {relative!r}")
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"unexpected binary tracked file: {relative!r}")
            continue
        for label, pattern in patterns:
            if pattern.search(text):
                errors.append(f"possible {label} in {relative!r}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        errors = validate(root)
    except RuntimeError as exc:
        print(f"public-tree validation failed: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("Public tree validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Public tree validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
