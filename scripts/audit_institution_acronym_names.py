#!/usr/bin/env python3
"""Validate conservative acronym-only institution naming decisions."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .curated_institutions import clean
    from .curated_schema import CURATED_DATA_DIR, REPOSITORY_ROOT
except ImportError:
    from curated_institutions import clean
    from curated_schema import CURATED_DATA_DIR, REPOSITORY_ROOT


DECISIONS_PATH = REPOSITORY_ROOT / "data/manual/institution_acronym_name_decisions.csv"
AUDIT_PATH = REPOSITORY_ROOT / "data/processed/institution_acronym_name_audit.csv"
SUMMARY_PATH = REPOSITORY_ROOT / "data/processed/institution_acronym_name_audit_summary.json"
DECISION_COLUMNS = (
    "institution_id", "original_canonical_name", "decision", "full_english_name",
    "abbreviation", "evidence", "notes",
)
AUDIT_COLUMNS = (
    *DECISION_COLUMNS, "current_canonical_name", "current_abbreviation",
    "institution_status", "validation_status",
)
ACRONYM_ONLY = re.compile(r"^(?=.*[A-Z])[A-Z0-9&.+*-]{2,20}$")


def read_csv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return tuple(reader.fieldnames or ()), [dict(row) for row in reader]


def write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def build_audit(
    institutions: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, str]], list[str]]:
    by_id = {clean(row.get("institution_id")): row for row in institutions}
    active_candidates = {
        clean(row.get("institution_id"))
        for row in institutions
        if clean(row.get("institution_status")) == "active"
        and ACRONYM_ONLY.fullmatch(clean(row.get("canonical_name")))
    }
    decided_ids: set[str] = set()
    issues: list[str] = []
    audit: list[dict[str, str]] = []
    for line, decision_row in enumerate(decisions, 2):
        decision = {column: clean(decision_row.get(column)) for column in DECISION_COLUMNS}
        institution_id = decision["institution_id"]
        current = by_id.get(institution_id)
        if not institution_id or institution_id in decided_ids:
            issues.append(f"decisions line {line}: missing or duplicate institution_id")
            continue
        decided_ids.add(institution_id)
        if decision["decision"] not in {"expanded", "intentional_brand", "merged"}:
            issues.append(f"{institution_id}: unsupported decision {decision['decision']!r}")
        if not ACRONYM_ONLY.fullmatch(decision["original_canonical_name"]):
            issues.append(f"{institution_id}: original name is not an acronym-only candidate")
        if not current:
            issues.append(f"{institution_id}: registry record is missing")
            continue
        current_name = clean(current.get("canonical_name"))
        current_abbreviation = clean(current.get("abbreviation"))
        status = clean(current.get("institution_status"))
        valid = True
        if decision["decision"] == "expanded":
            valid = (
                status == "active"
                and current_name == decision["full_english_name"]
                and current_abbreviation == decision["abbreviation"]
                and current_name != decision["original_canonical_name"]
            )
        elif decision["decision"] == "intentional_brand":
            valid = status == "active" and current_name == decision["original_canonical_name"]
        elif decision["decision"] == "merged":
            valid = status == "merged"
        if not valid:
            issues.append(f"{institution_id}: registry state does not match {decision['decision']}")
        audit.append({
            **decision,
            "current_canonical_name": current_name,
            "current_abbreviation": current_abbreviation,
            "institution_status": status,
            "validation_status": "resolved" if valid else "invalid",
        })
    missing = sorted(active_candidates - decided_ids)
    if missing:
        issues.append("unreviewed active acronym candidates: " + ", ".join(missing))
    return audit, issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--institutions", type=Path, default=CURATED_DATA_DIR / "institutions.csv")
    parser.add_argument("--decisions", type=Path, default=DECISIONS_PATH)
    parser.add_argument("--audit-output", type=Path, default=AUDIT_PATH)
    parser.add_argument("--summary-output", type=Path, default=SUMMARY_PATH)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    institution_columns, institutions = read_csv(arguments.institutions)
    if "abbreviation" not in institution_columns:
        raise SystemExit("institutions registry has no abbreviation field")
    decision_columns, decisions = read_csv(arguments.decisions)
    if decision_columns != DECISION_COLUMNS:
        raise SystemExit(f"{arguments.decisions} has an unexpected header")
    audit, issues = build_audit(institutions, decisions)
    summary = {
        "active_canonical_institutions": sum(
            clean(row.get("institution_status")) == "active" for row in institutions
        ),
        "acronym_only_candidates_audited": len(audit),
        "expanded": sum(row["decision"] == "expanded" for row in audit),
        "intentional_standalone_brands": sum(
            row["decision"] == "intentional_brand" for row in audit
        ),
        "merged": sum(row["decision"] == "merged" for row in audit),
        "unresolved": len(issues),
        "issues": issues,
    }
    if not arguments.check:
        write_csv(arguments.audit_output, AUDIT_COLUMNS, audit)
        arguments.summary_output.parent.mkdir(parents=True, exist_ok=True)
        arguments.summary_output.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
