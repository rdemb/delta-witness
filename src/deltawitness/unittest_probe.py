"""A cooperating standard-library unittest adapter that emits typed receipts."""

from __future__ import annotations

import argparse
import io
import os
from pathlib import Path
import sys
import unittest

from . import __version__
from .errors import ReceiptError
from .receipt import build_receipt_document, classify_counts, write_outcome_receipt

_RECEIPT_PATH_ENV = "DELTAWITNESS_RECEIPT_PATH"
_RECEIPT_BINDING_ENV = "DELTAWITNESS_RECEIPT_BINDING"
_PRODUCER_NAME = "deltawitness-unittest"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deltawitness-unittest",
        description="Run unittest discovery and emit a DeltaWitness outcome receipt.",
    )
    parser.add_argument(
        "--start-directory",
        default="tests",
        help="Directory in which discovery starts (default: tests)",
    )
    parser.add_argument(
        "--pattern",
        default="test*.py",
        help="Discovery filename pattern (default: test*.py)",
    )
    parser.add_argument(
        "--top-level-directory",
        default=None,
        help="Optional project top-level directory passed to unittest discovery",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        choices=(0, 1, 2),
        default=1,
        help="Internal unittest verbosity; raw output is not placed in the receipt",
    )
    return parser


def _destination_from_environment() -> tuple[Path, str]:
    raw_path = os.environ.get(_RECEIPT_PATH_ENV)
    binding = os.environ.get(_RECEIPT_BINDING_ENV)
    if not raw_path or not binding:
        raise ReceiptError(
            "missing_environment",
            "The unittest receipt adapter must run under a receipt-aware DeltaWitness claim",
        )
    path = Path(raw_path)
    if not path.is_absolute():
        raise ReceiptError("invalid_path", "Outcome receipt path must be absolute")
    return path, binding


def _zero_counts() -> dict[str, int]:
    return {
        "tests_run": 0,
        "passed": 0,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "expected_failures": 0,
        "unexpected_successes": 0,
    }


def _counts_from_result(result: unittest.TestResult) -> dict[str, int]:
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(getattr(result, "skipped", ()))
    expected_failures = len(getattr(result, "expectedFailures", ()))
    unexpected_successes = len(getattr(result, "unexpectedSuccesses", ()))
    tests_run = int(result.testsRun)
    passed = tests_run - failures - errors - skipped - expected_failures - unexpected_successes
    if passed < 0:
        raise ReceiptError(
            "inconsistent_result",
            "unittest result categories exceed testsRun",
        )
    return {
        "tests_run": tests_run,
        "passed": passed,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "expected_failures": expected_failures,
        "unexpected_successes": unexpected_successes,
    }


def _write(
    destination: Path,
    binding: str,
    *,
    outcome: str,
    counts: dict[str, int],
) -> None:
    document = build_receipt_document(
        binding=binding,
        producer_name=_PRODUCER_NAME,
        producer_version=__version__,
        outcome=outcome,
        counts=counts,
    )
    write_outcome_receipt(destination, document, expected_binding=binding)


def run_probe(args: argparse.Namespace) -> int:
    destination, binding = _destination_from_environment()
    try:
        loader = unittest.TestLoader()
        suite = loader.discover(
            start_dir=args.start_directory,
            pattern=args.pattern,
            top_level_dir=args.top_level_directory,
        )
        stream = io.StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=args.verbosity,
            failfast=False,
            buffer=True,
        )
        result = runner.run(suite)
        counts = _counts_from_result(result)
        outcome = classify_counts(counts)
        _write(destination, binding, outcome=outcome, counts=counts)
    except ReceiptError:
        raise
    except Exception as exc:
        try:
            _write(
                destination,
                binding,
                outcome="producer_error",
                counts=_zero_counts(),
            )
        except Exception:
            pass
        raise ReceiptError("producer_error", "unittest receipt production failed") from exc

    if outcome == "passed":
        return 0
    if outcome == "test_failure":
        return 1
    return 2


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return run_probe(args)
    except ReceiptError as exc:
        print(f"DeltaWitness unittest receipt error: {exc.code}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
