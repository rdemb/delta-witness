"""Command execution with conservative environment handling."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
from typing import Sequence

from .errors import VerificationError

_OUTPUT_PREVIEW_LIMIT = 20_000
_PRESERVED_ENV = (
    "PATH",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
)


@dataclass(frozen=True)
class ProcessObservation:
    return_code: int | None
    duration_seconds: float
    timed_out: bool
    stdout_sha256: str
    stderr_sha256: str
    stdout: str | None
    stderr: str | None


def _isolated_environment(
    state: str,
    worktree: Path,
    runtime_root: Path,
    pass_env: Sequence[str],
) -> dict[str, str]:
    env: dict[str, str] = {}
    for name in _PRESERVED_ENV:
        value = os.environ.get(name)
        if value is not None:
            env[name] = value
    env.setdefault("PATH", os.defpath)

    for name in pass_env:
        if name not in os.environ:
            raise VerificationError(f"Requested environment variable is not set: {name}")
        env[name] = os.environ[name]

    home = runtime_root / "home"
    temp = runtime_root / "tmp"
    cache = runtime_root / "cache"
    config = runtime_root / "config"
    data = runtime_root / "data"
    for directory in (home, temp, cache, config, data):
        directory.mkdir(parents=True, exist_ok=True)

    env.update(
        {
            "CI": "true",
            "TZ": "UTC",
            "PYTHONHASHSEED": "0",
            "HOME": str(home),
            "USERPROFILE": str(home),
            "TMPDIR": str(temp),
            "TMP": str(temp),
            "TEMP": str(temp),
            "XDG_CACHE_HOME": str(cache),
            "XDG_CONFIG_HOME": str(config),
            "XDG_DATA_HOME": str(data),
            "DELTAWITNESS_STATE": state,
            "DELTAWITNESS_WORKTREE": str(worktree),
        }
    )
    return env


def _digest_and_preview(stream: object, include_output: bool) -> tuple[str, str | None]:
    stream.seek(0)  # type: ignore[attr-defined]
    digest = hashlib.sha256()
    preview = bytearray()
    total_size = 0
    while True:
        chunk = stream.read(65_536)  # type: ignore[attr-defined]
        if not chunk:
            break
        total_size += len(chunk)
        digest.update(chunk)
        if include_output and len(preview) < _OUTPUT_PREVIEW_LIMIT:
            remaining = _OUTPUT_PREVIEW_LIMIT - len(preview)
            preview.extend(chunk[:remaining])
    rendered: str | None = None
    if include_output:
        rendered = bytes(preview).decode("utf-8", errors="replace")
        if total_size > _OUTPUT_PREVIEW_LIMIT:
            rendered += "\n...[preview truncated by DeltaWitness]"
    return digest.hexdigest(), rendered


def _terminate_process_tree(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        process.kill()


def run_command(
    command: Sequence[str],
    *,
    state: str,
    cwd: Path,
    timeout_seconds: int,
    pass_env: Sequence[str],
    include_output: bool,
) -> ProcessObservation:
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="deltawitness-runtime-") as runtime_directory:
        runtime_root = Path(runtime_directory)
        env = _isolated_environment(state, cwd, runtime_root, pass_env)
        with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
            try:
                process = subprocess.Popen(
                    list(command),
                    cwd=cwd,
                    env=env,
                    stdin=subprocess.DEVNULL,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    shell=False,
                    start_new_session=(os.name == "posix"),
                )
            except OSError as exc:
                raise VerificationError(f"Cannot execute command {command!r}: {exc}") from exc

            timed_out = False
            try:
                process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                _terminate_process_tree(process)
                process.wait()

            duration = time.monotonic() - started
            stdout_sha256, stdout = _digest_and_preview(stdout_file, include_output)
            stderr_sha256, stderr = _digest_and_preview(stderr_file, include_output)
            return ProcessObservation(
                return_code=None if timed_out else process.returncode,
                duration_seconds=round(duration, 6),
                timed_out=timed_out,
                stdout_sha256=stdout_sha256,
                stderr_sha256=stderr_sha256,
                stdout=stdout,
                stderr=stderr,
            )
