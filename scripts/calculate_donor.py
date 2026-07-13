#!/usr/bin/env python3
"""Calculate deterministic donor policy results from JSON or legacy CSV."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from donor_policy import DonorPolicyError, reconcile_donor_record


def _date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministically reconcile donor arithmetic using only the Python "
            "standard library. Emits JSON and never generates or sends letters."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("donor", "process one donor JSON object"),
        ("csv", "process donor rows from a legacy-compatible CSV"),
    ):
        subparser = subparsers.add_parser(command, help=help_text)
        subparser.add_argument("--input", required=True, type=Path, help="input file path")
        subparser.add_argument(
            "--as-of-date", required=True, type=_date, help="campaign date (YYYY-MM-DD)"
        )
        subparser.add_argument(
            "--campaign-type", required=True, help="for example: Annual Fund"
        )
    return parser


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DonorPolicyError("unable to read a valid donor JSON object") from exc
    if not isinstance(value, dict):
        raise DonorPolicyError("donor JSON input must contain one object")
    return value


def _load_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise DonorPolicyError("CSV input is missing a header row")
            rows = list(reader)
    except DonorPolicyError:
        raise
    except (OSError, UnicodeError, csv.Error) as exc:
        raise DonorPolicyError("unable to read valid donor CSV input") from exc
    return rows


def run(args: argparse.Namespace) -> dict[str, Any] | list[dict[str, Any]]:
    if args.command == "donor":
        return reconcile_donor_record(
            _load_json(args.input), args.as_of_date, args.campaign_type
        )
    return [
        reconcile_donor_record(row, args.as_of_date, args.campaign_type)
        for row in _load_csv(args.input)
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except DonorPolicyError as exc:
        # Diagnostics deliberately omit raw records and donor PII.
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

