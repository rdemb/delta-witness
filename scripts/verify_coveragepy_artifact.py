#!/usr/bin/env python3
"""Verify the exact research-only Coverage.py wheel before installation."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from deltawitness.coveragepy_contract import (
    COVERAGEPY_WHEEL_FILENAME,
    CoveragePyArtifactAccessError,
    CoveragePyContractError,
    verify_coveragepy_artifact,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Verify the exact Coverage.py universal wheel authorized for the "
            "DW-001 research baseline."
        )
    )
    parser.add_argument("artifact", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        digest = verify_coveragepy_artifact(args.artifact)
    except CoveragePyArtifactAccessError as exc:
        print(f"Coverage.py artifact verification failed: {exc}", file=sys.stderr)
        return 2
    except CoveragePyContractError as exc:
        print(f"Coverage.py artifact verification failed: {exc}", file=sys.stderr)
        return 1
    print(
        "Coverage.py artifact verified: "
        f"{COVERAGEPY_WHEEL_FILENAME} sha256={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
