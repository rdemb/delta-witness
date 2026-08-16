"""A cooperating standard-library unittest adapter that emits typed receipts."""

from __future__ import annotations

import argparse
from collections import Counter
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
_OUTCOME_PRECEDENCE = {
    "passed": 0,
    "expected_failure": 1,
    "skipped": 2,
    "failure": 3,
    "unexpected_success": 4,
    "error": 5,
}


class _ReceiptTestResult(unittest.TextTestResult):
    """Track one conservative final category per logical unittest test object."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        # The object is retained alongside its identity key. Storing only id(test)
        # would permit CPython to reuse that integer after an executed test object
        # is released by a cleaning TestSuite, silently merging unrelated outcomes.
        self._logical_outcomes: dict[int, tuple[object, str]] = {}

    def _record(self, test: object, outcome: str) -> None:
        key = id(test)
        previous = self._logical_outcomes.get(key)
        if previous is not None and previous[0] is not test:
            raise ReceiptError(
                "test_identity_collision",
                "A logical unittest object identity was reused during one receipt run",
            )
        previous_outcome = previous[1] if previous is not None else None
        if (
            previous_outcome is None
            or _OUTCOME_PRECEDENCE[outcome] > _OUTCOME_PRECEDENCE[previous_outcome]
        ):
            self._logical_outcomes[key] = (test, outcome)

    def startTest(self, test: unittest.case.TestCase) -> None:  # noqa: N802 - unittest API
        self._record(test, "passed")
        super().startTest(test)

    def addSuccess(self, test: unittest.case.TestCase) -> None:  # noqa: N802 - unittest API
        self._record(test, "passed")
        super().addSuccess(test)

    def addFailure(
        self,
        test: unittest.case.TestCase,
        err: tuple[type[BaseException], BaseException, object],
    ) -> None:  # noqa: N802 - unittest API
        self._record(test, "failure")
        super().addFailure(test, err)  # type: ignore[arg-type]

    def addError(
        self,
        test: unittest.case.TestCase,
        err: tuple[type[BaseException], BaseException, object],
    ) -> None:  # noqa: N802 - unittest API
        self._record(test, "error")
        super().addError(test, err)  # type: ignore[arg-type]

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:  # noqa: N802 - unittest API
        self._record(test, "skipped")
        super().addSkip(test, reason)

    def addExpectedFailure(
        self,
        test: unittest.case.TestCase,
        err: tuple[type[BaseException], BaseException, object],
    ) -> None:  # noqa: N802 - unittest API
        self._record(test, "expected_failure")
        super().addExpectedFailure(test, err)  # type: ignore[arg-type]

    def addUnexpectedSuccess(self, test: unittest.case.TestCase) -> None:  # noqa: N802 - unittest API
        self._record(test, "unexpected_success")
        super().addUnexpectedSuccess(test)

    def addSubTest(
        self,
        test: unittest.case.TestCase,
        subtest: unittest.case.TestCase,
        err: tuple[type[BaseException], BaseException, object] | None,
    ) -> None:  # noqa: N802 - unittest API
        if err is not None:
            failure_type = getattr(test, "failureException", AssertionError)
            outcome = "failure" if issubclass(err[0], failure_type) else "error"
            self._record(test, outcome)
        super().addSubTest(test, subtest, err)  # type: ignore[arg-type]

    def receipt_counts(self) -> dict[str, int]:
        categories = Counter(outcome for _, outcome in self._logical_outcomes.values())
        return {
            "tests_run": len(self._logical_outcomes),
            "passed": categories["passed"],
            "failures": categories["failure"],
            "errors": categories["error"],
            "skipped": categories["skipped"],
            "expected_failures": categories["expected_failure"],
            "unexpected_successes": categories["unexpected_success"],
        }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deltawitness-unittest",
        description=(
            "Run unittest discovery or exact dotted logical-test selectors and "
            "emit a DeltaWitness outcome receipt."
        ),
    )
    parser.add_argument(
        "--start-directory",
        default="tests",
        help="Directory in which discovery or dotted-name loading starts (default: tests)",
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
        "--test-name",
        action="append",
        default=None,
        help=(
            "Exact dotted unittest logical-test name. May be repeated; when "
            "present, discovery pattern and top-level directory are not used."
        ),
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


def _load_suite(args: argparse.Namespace) -> unittest.TestSuite:
    loader = unittest.TestLoader()
    if args.test_name:
        start_directory = Path(args.start_directory)
        try:
            resolved_start = start_directory.resolve(strict=True)
        except OSError as exc:
            raise ReceiptError(
                "invalid_start_directory",
                "The unittest selector start directory cannot be resolved",
            ) from exc
        if not resolved_start.is_dir():
            raise ReceiptError(
                "invalid_start_directory",
                "The unittest selector start directory must be a directory",
            )
        sys.path.insert(0, str(resolved_start))
        return loader.loadTestsFromNames(args.test_name)
    return loader.discover(
        start_dir=args.start_directory,
        pattern=args.pattern,
        top_level_dir=args.top_level_directory,
    )


def run_probe(args: argparse.Namespace) -> int:
    destination, binding = _destination_from_environment()
    try:
        suite = _load_suite(args)
        stream = io.StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=args.verbosity,
            failfast=False,
            buffer=True,
            resultclass=_ReceiptTestResult,
        )
        result = runner.run(suite)
        if not isinstance(result, _ReceiptTestResult):
            raise ReceiptError("unexpected_result", "unittest returned an unexpected result type")
        counts = result.receipt_counts()
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
