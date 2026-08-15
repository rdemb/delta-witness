"""Command-line interface for DeltaWitness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .config import load_config
from .errors import DeltaWitnessError, UnsupportedClaimError
from .gitops import find_repo_root, git_metadata_path, git_version
from .influence import (
    InfluenceReport,
    analyze_patch_influence,
    influence_report_to_dict,
    write_influence_report,
)
from .matrix import VerificationReport, report_to_dict, verify_repository, write_report
from .reporting import load_report, verify_report_document


def _add_common_verification_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--base", required=True, help="Base Git ref, for example origin/main")
    parser.add_argument("--head", default="HEAD", help="Candidate Git ref (default: HEAD)")
    parser.add_argument("--spec", type=Path, default=Path("deltawitness.toml"))
    parser.add_argument("--json", action="store_true", help="Print the complete JSON report")
    parser.add_argument(
        "--include-output",
        action="store_true",
        help="Include bounded stdout/stderr previews in the report; may expose sensitive data",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deltawitness",
        description="Counterfactual verification for AI-generated code changes.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check local prerequisites and safety mode")
    doctor.add_argument("--repo", type=Path, default=Path.cwd())

    verify = subparsers.add_parser("verify", help="Run the four-state counterfactual matrix")
    _add_common_verification_arguments(verify)
    verify.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Report path. Defaults to the repository's private Git metadata directory.",
    )

    influence = subparsers.add_parser(
        "influence",
        help="Enumerate exact code-path coalitions and attribute witness influence",
    )
    _add_common_verification_arguments(influence)
    influence.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Influence report path. Defaults to private Git metadata.",
    )

    verify_report = subparsers.add_parser(
        "verify-report",
        help="Verify matrix or patch-influence report integrity digests",
    )
    verify_report.add_argument("report", type=Path)

    return parser


def _doctor(repo_argument: Path) -> int:
    repo = find_repo_root(repo_argument)
    print(f"DeltaWitness: {__version__}")
    print(f"Git: {git_version()}")
    print(f"Repository: {repo}")
    print("Command environment: sanitized")
    print("Observers: exit-code-v1, outcome-receipt-v1")
    print("Exact patch influence: available for up to 8 changed code paths")
    print("Raw command output: excluded by default")
    print("Filesystem and network sandbox: unavailable")
    print("Status: prerequisites satisfied for trusted-code research runs")
    return 0


def _render_report(report: VerificationReport) -> None:
    print("\nDeltaWitness counterfactual matrix")
    print("=" * 36)
    for claim in report.claims:
        print(f"\nClaim: {claim.claim_id}")
        if claim.description:
            print(f"  {claim.description}")
        print(f"  observer: {claim.observer}")
        for state in claim.states:
            marker = "OK" if state.matched else "NO"
            print(
                f"  [{marker}] {state.state:<20} "
                f"expected={state.expected:<4} observed={state.observed:<7} "
                f"exit={state.return_code}"
            )
            if state.observer == "outcome-receipt-v1":
                receipt = state.receipt_outcome or "unavailable"
                producer = (
                    state.receipt_producer.get("name", "unknown")
                    if state.receipt_producer is not None
                    else "unavailable"
                )
                print(f"       receipt={receipt} producer={producer}")
            if state.observation_error:
                print(f"       observer_error={state.observation_error}")
        if any(state.observed in {"timeout", "error"} for state in claim.states):
            verdict = "INCOMPLETE"
        else:
            verdict = "SUPPORTED_IN_SCOPE" if claim.supported else "UNSUPPORTED"
        print(f"  verdict: {verdict}")
    overall = "INCOMPLETE" if not report.complete else (
        "SUPPORTED_IN_SCOPE" if report.supported else "UNSUPPORTED"
    )
    print("\nOverall verdict:", overall)
    print("Witness SHA-256:", report.witness_sha256)
    print("Report SHA-256:", report.report_sha256)


def _fraction_decimal(document: object) -> str:
    if not isinstance(document, dict):
        return "unavailable"
    value = document.get("decimal")
    return f"{value:.6f}" if isinstance(value, (int, float)) else "unavailable"


def _render_influence(report: InfluenceReport) -> None:
    print("\nDeltaWitness exact patch influence")
    print("=" * 38)
    print("Status:", report.status)
    print("Code paths:", report.intervention["path_count"])
    print("Coalitions:", report.intervention["coalition_count"])
    print("Complete table:", report.complete)
    print("Endpoint anchors consistent:", report.anchors_consistent)

    for anchor in report.anchors:
        marker = "OK" if anchor["consistent"] else "NO"
        print(
            f"  [{marker}] {anchor['name']}: "
            f"outcomes={anchor['outcomes_match']} tree={anchor['tree_match']} "
            f"required={anchor['tree_required']}"
        )

    if report.metrics is None:
        indeterminate = sum(1 for coalition in report.coalitions if not coalition.complete)
        print("Attribution metrics: unavailable")
        print("Indeterminate coalitions:", indeterminate)
    else:
        minimal = report.metrics["minimal_supported_coalitions"]
        print("Supported coalitions:", report.metrics["supported_coalition_count"])
        print("Minimal witness-sufficient coalitions:", len(minimal))
        for coalition in minimal:
            paths = ", ".join(coalition["paths"]) or "<empty>"
            print(f"  - {coalition['coalition_id']}: {paths}")
        print("Monotone non-decreasing:", report.metrics["monotone_non_decreasing"])
        print("\nPath influence:")
        for path in report.metrics["paths"]:
            print(
                f"  {path['path']}\n"
                f"    Shapley={_fraction_decimal(path['shapley'])} "
                f"Banzhaf={_fraction_decimal(path['normalized_banzhaf'])} "
                f"positive={path['positive_swings']} negative={path['negative_swings']}\n"
                f"    globally_necessary={path['globally_necessary']} "
                f"full_context_necessary={path['full_context_necessary']} "
                f"standalone_sufficient={path['standalone_sufficient']}"
            )

    print("\nInfluence SHA-256:", report.influence_sha256)
    print("Report SHA-256:", report.report_sha256)


def _verify(args: argparse.Namespace) -> int:
    repo = find_repo_root(args.repo)
    spec_path = args.spec if args.spec.is_absolute() else repo / args.spec
    if args.output is None:
        output_path = git_metadata_path(repo, "deltawitness/report.json")
    else:
        output_path = args.output if args.output.is_absolute() else repo / args.output
    config = load_config(spec_path)
    report = verify_repository(
        repo,
        args.base,
        args.head,
        config,
        include_output=args.include_output,
    )
    write_report(report, output_path)
    if args.json:
        print(json.dumps(report_to_dict(report), indent=2, sort_keys=True))
    else:
        _render_report(report)
        print(f"Report written to: {output_path}")
    if not report.complete:
        return 2
    return 0 if report.supported else 1


def _influence(args: argparse.Namespace) -> int:
    repo = find_repo_root(args.repo)
    spec_path = args.spec if args.spec.is_absolute() else repo / args.spec
    if args.output is None:
        output_path = git_metadata_path(repo, "deltawitness/influence.json")
    else:
        output_path = args.output if args.output.is_absolute() else repo / args.output
    config = load_config(spec_path)
    report = analyze_patch_influence(
        repo,
        args.base,
        args.head,
        config,
        include_output=args.include_output,
    )
    write_influence_report(report, output_path)
    if args.json:
        print(json.dumps(influence_report_to_dict(report), indent=2, sort_keys=True))
    else:
        _render_influence(report)
        print(f"Report written to: {output_path}")
    return 0 if report.attribution_available else 2


def _verify_report(path: Path) -> int:
    document = load_report(path.resolve())
    valid, errors = verify_report_document(document)
    if valid:
        print("Report integrity: VALID")
        if "influence_sha256" in document:
            print("Influence SHA-256:", document["influence_sha256"])
        else:
            print("Witness SHA-256:", document["witness_sha256"])
        print("Report SHA-256:", document["report_sha256"])
        return 0
    print("Report integrity: INVALID", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            return _doctor(args.repo)
        if args.command == "verify":
            return _verify(args)
        if args.command == "influence":
            return _influence(args)
        if args.command == "verify-report":
            return _verify_report(args.report)
        parser.error(f"Unknown command: {args.command}")
    except UnsupportedClaimError as exc:
        print(f"DeltaWitness unsupported: {exc}", file=sys.stderr)
        return 1
    except DeltaWitnessError as exc:
        print(f"DeltaWitness error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
