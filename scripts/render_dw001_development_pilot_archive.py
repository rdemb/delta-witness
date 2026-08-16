#!/usr/bin/env python3
"""Execute the committed DW-001 development plan and emit a verified archive.

The default mode writes one canonical JSON archive to an explicit output path.
The optional ``--gzip-base64-stdout`` mode is intended only for a reviewed,
public-safe synthetic bundle when repository tooling cannot retain a multi-file
bundle directly. It performs no network operation itself and emits no raw test
output, source code, credentials, environment values, or absolute paths.

This script does not authorize a holdout or confirmatory interpretation.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import json
from pathlib import Path
import tempfile

from deltawitness.dw001_pilot import (
    build_development_pilot_archive,
    run_development_pilot,
    verify_development_pilot_archive_document,
)
from deltawitness.reporting import load_report


_DEFAULT_PLAN = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "DW-001"
    / "development-pilot-plan.v1.json"
)
_CHUNK_SIZE = 6000
_BEGIN = "DW001_CANONICAL_ARCHIVE_BEGIN"
_CHUNK = "DW001_CANONICAL_ARCHIVE_CHUNK"
_END = "DW001_CANONICAL_ARCHIVE_END"


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=_DEFAULT_PLAN)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--gzip-base64-stdout", action="store_true")
    arguments = parser.parse_args()
    if (arguments.output is None) == (not arguments.gzip_base64_stdout):
        parser.error("choose exactly one of --output or --gzip-base64-stdout")
    return arguments


def _canonical_bytes(document: object) -> bytes:
    return json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _emit_chunks(payload: str, *, archive: dict[str, object], raw_size: int) -> None:
    chunks = [
        payload[offset : offset + _CHUNK_SIZE]
        for offset in range(0, len(payload), _CHUNK_SIZE)
    ]
    print(
        f"{_BEGIN} archive_sha256={archive['archive_sha256']} "
        f"semantic_sha256={archive['index_semantic_sha256']} "
        f"raw_bytes={raw_size} chunks={len(chunks)}"
    )
    for index, chunk in enumerate(chunks, start=1):
        print(f"{_CHUNK} {index:04d}/{len(chunks):04d} {chunk}")
    print(f"{_END} archive_sha256={archive['archive_sha256']}")


def main() -> int:
    arguments = _arguments()
    plan = load_report(arguments.plan)
    with tempfile.TemporaryDirectory(prefix="deltawitness-canonical-pilot-") as directory:
        bundle = Path(directory) / "bundle"
        run_development_pilot(plan, bundle)
        archive = build_development_pilot_archive(bundle, plan)
    valid, errors = verify_development_pilot_archive_document(archive, plan)
    if not valid:
        raise AssertionError(errors)

    raw = _canonical_bytes(archive)
    if arguments.output is not None:
        output = arguments.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(
            json.dumps(
                archive,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            ).encode("utf-8")
            + b"\n"
        )
        print(
            "DW-001 canonical development pilot archive written: "
            f"sha256={archive['archive_sha256']} bytes={output.stat().st_size}"
        )
        return 0

    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    payload = base64.b64encode(compressed).decode("ascii")
    _emit_chunks(payload, archive=archive, raw_size=len(raw))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
