#!/usr/bin/env python3
"""Build the bounded, non-destructive 76-paper legacy-scope audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.legacy_scope_cleanup_audit import (  # noqa: E402
    ARTIFACT_HASH_PATH,
    CATEGORY_BY_DIAGNOSTIC,
    CSV_PATH,
    DIAGNOSTIC_PATH,
    FIELDS,
    HIGH_CONFIDENCE_PATH,
    IDENTITY_SUMMARY_PATH,
    NEEDS_REVIEW_PATH,
    OUT,
    REPORT_PATH,
    VALIDATION_PATH,
    arxiv_id,
    canonical_csv_text,
    expected_identity_match_method,
    expected_identity_status,
    expected_public_identity,
    generated_texts,
    legacy_public_records,
    normalize_doi,
    normalize_title,
    openalex_id,
    public_match,
    read_csv,
    taxonomy_text,
    validate_rows,
    verify_baseline,
    verify_workspace_scope,
)


RECOVERY_DIR = ROOT / "data/processed/legacy_scope_cleanup_audit_2026_09"
RECOVERED_EVIDENCE_PATHS = (
    RECOVERY_DIR / "recovered_deepfake_rows_003_035.json",
    RECOVERY_DIR / "recovered_deepfake_rows_036_071.json",
    RECOVERY_DIR / "recovered_categories_and_tail.json",
)

FRAME_LEVEL = {
    "curated:074bb9a77ee85d50090c",
    "curated:6a0913decc4e81abddb3",
    "curated:80e6fc4ce64c001a2b3d",
    "curated:8227355571a6d402e4f8",
    "curated:a0c532923fe10a4ee7c0",
    "curated:bbe4e9e8c5b41e467a76",
    "curated:cd18fc45f8a86a30aaf6",
    "doi:10.1016/j.procs.2023.01.237",
    "doi:10.1016/j.procs.2025.04.313",
    "doi:10.1016/j.patrec.2024.03.025",
    "doi:10.1109/cvpr42600.2020.00505",
    "doi:10.1109/tpami.2021.3093446",
    "doi:10.1145/3512732.3533582",
    "doi:10.23919/ccc50068.2020.9189596",
}
TEMPORAL_VIDEO = {
    "doi:10.1109/idicaiei61867.2024.10842840",
    "doi:10.3390/electronics13091662",
}
VIDEO_LEVEL_FRAME = {"doi:10.1016/j.heliyon.2024.e37163"}
SURVEYS = {
    "curated:c071c25bc2957d78569b",
    "doi:10.1002/widm.1520",
    "doi:10.1109/hora55278.2022.9799858",
}


def load_recovered_evidence() -> dict[str, dict[str, str]]:
    records: list[dict[str, str]] = []
    for path in RECOVERED_EVIDENCE_PATHS:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise AssertionError(f"{path} must contain a JSON array")
        records.extend(payload)
    by_identity: dict[str, dict[str, str]] = {}
    for record in records:
        identity = record["paper_identity"]
        if identity in by_identity:
            raise AssertionError(f"duplicate recovered evidence: {identity}")
        by_identity[identity] = record
    return by_identity


def strong_identifiers_agree(
    diagnostic: Mapping[str, str],
    public: Mapping[str, object],
    all_public: Sequence[Mapping[str, object]],
) -> bool:
    checks: list[tuple[str, str]] = []
    paper_id = diagnostic.get("paper_id", "").strip()
    doi = normalize_doi(diagnostic.get("doi") or public.get("doi"))
    diagnostic_arxiv = arxiv_id(diagnostic.get("primary_url"))
    diagnostic_openalex = openalex_id(diagnostic.get("primary_url"))
    public_arxiv = str(public.get("arxiv_id") or "").strip()
    public_openalex = openalex_id(public.get("openalex_url"))
    if paper_id:
        checks.append(("paper_id", paper_id))
    if doi:
        checks.append(("doi", doi))
    if diagnostic_arxiv:
        checks.append(("arxiv_id", diagnostic_arxiv))
    if diagnostic_openalex:
        checks.append(("openalex_id", diagnostic_openalex))
    if public_arxiv:
        checks.append(("arxiv_id", public_arxiv))
    if public_openalex:
        checks.append(("openalex_id", public_openalex))

    for kind, value in checks:
        matches = []
        for candidate in all_public:
            current = {
                "paper_id": str(candidate.get("paper_id") or ""),
                "doi": normalize_doi(candidate.get("doi")),
                "arxiv_id": str(candidate.get("arxiv_id") or "").strip(),
                "openalex_id": openalex_id(candidate.get("openalex_url")),
            }[kind]
            if current == value:
                matches.append(candidate)
        if len(matches) != 1 or matches[0] is not public:
            return False
    return bool(checks)


def media_fields(
    candidate: Mapping[str, str], review: Mapping[str, str]
) -> tuple[str, str, str]:
    category = CATEGORY_BY_DIAGNOSTIC[candidate["legacy_scope_category"]]
    identity = candidate["paper_identity"]
    status = review["final_audit_status"]
    if category == "watermark_provenance":
        return (
            "not_applicable",
            "no",
            "temporal cues required=no; video-level evaluation=no; frames sampled=no; "
            "independent still-image inference=yes; non-face synthetic images evaluated=yes",
        )
    if category == "classical_manipulation":
        return (
            "not_applicable",
            "no",
            "temporal cues required=no; video-level evaluation=no; frames sampled=no; "
            "independent still-image inference=yes; non-face synthetic images evaluated=no "
            "(classical manipulations only)",
        )
    if status == "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW":
        return (
            "unclear",
            "unclear",
            "temporal-cue requirement=unclear; video-level evaluation=unclear; "
            "frame sampling=unclear; independent still-image inference=unclear; "
            "non-face synthetic-image evaluation=unclear",
        )
    if status == "LEGACY_KEEP_IN_SCOPE":
        if identity == "curated:fe42bad5f72f9f6858c5":
            return (
                "no",
                "mixed_independent_still",
                "qualifying image branch requires no temporal cues; separate video-level "
                "branch=yes; qualifying image branch samples no video frames; independent "
                "still-image inference=yes; non-face synthetic images evaluated=yes",
            )
        return (
            "no",
            "no",
            "temporal cues required=no; video-level evaluation=no; frames sampled=no; "
            "independent still-image inference=yes; non-face synthetic images evaluated=yes",
        )
    if identity in TEMPORAL_VIDEO:
        return (
            "yes",
            "yes",
            "temporal cues required=yes; video-level evaluation=yes; frames sampled=yes; "
            "independent still-image inference=no; non-face synthetic images evaluated=no",
        )
    if identity in VIDEO_LEVEL_FRAME:
        return (
            "yes",
            "yes",
            "temporal cues required=no; video-level application/evaluation=yes; frames "
            "sampled=yes; independent still-image benchmark=no; non-face synthetic images "
            "evaluated=no",
        )
    if identity in SURVEYS:
        return (
            "yes",
            "yes",
            "temporal cues required=not applicable (review); video-level literature "
            "covered=yes; frames sampled=not applicable; independent face-image literature "
            "covered=yes; non-face synthetic-image contribution=no",
        )
    if identity in FRAME_LEVEL:
        return (
            "yes",
            "yes",
            "temporal cues required=no; video-level evaluation=no (frame/image level); "
            "frames sampled=yes; independent still-image inference=yes (face images only); "
            "non-face synthetic images evaluated=no",
        )
    return (
        "yes",
        "no",
        "temporal cues required=no; video-level evaluation=no; frames sampled=no; "
        "independent still-image inference=yes (face images only); non-face synthetic "
        "images evaluated=no",
    )


def build_rows() -> list[dict[str, str]]:
    diagnostic = read_csv(DIAGNOSTIC_PATH)
    public_rows = legacy_public_records()
    recovered = load_recovered_evidence()
    expected_identities = [row["paper_identity"] for row in diagnostic]
    if len(diagnostic) != 76 or len(set(expected_identities)) != 76:
        raise AssertionError("frozen diagnostic is not exactly 76 unique candidates")
    if set(recovered) != set(expected_identities):
        raise AssertionError(
            "recovered evidence mismatch: missing="
            f"{sorted(set(expected_identities) - set(recovered))}; extra="
            f"{sorted(set(recovered) - set(expected_identities))}"
        )

    rows = []
    for candidate in diagnostic:
        review = recovered[candidate["paper_identity"]]
        public = public_match(candidate, public_rows)
        if review["title"] != candidate["canonical_title"]:
            raise AssertionError(f"evidence title mismatch: {candidate['paper_identity']}")
        agrees = strong_identifiers_agree(candidate, public, public_rows)
        identity_status = expected_identity_status(candidate, public)
        if not agrees:
            identity_status = "IDENTITY_RESOLUTION_REQUIRED"
        exact_question = review.get("exact_evidence_needed") or ""
        if review["final_audit_status"] != "LEGACY_SCOPE_DRIFT_NEEDS_REVIEW":
            exact_question = ""
        face_flag, video_flag, media_status = media_fields(candidate, review)
        row = {
            "source_diagnostic_row_id": candidate["legacy_review_id"],
            "candidate_identity": candidate["paper_identity"],
            "paper_id": candidate["paper_id"],
            "title": candidate["canonical_title"],
            "year": candidate["year"],
            "doi": normalize_doi(candidate["doi"] or public.get("doi")),
            "arxiv_id": str(public.get("arxiv_id") or "").strip(),
            "openalex_id": openalex_id(public.get("openalex_url")),
            "resolved_authoritative_identity": expected_public_identity(public),
            "normalized_title_identity": (
                f"title-year:{normalize_title(candidate['canonical_title'])}|"
                f"{candidate['year']}"
            ),
            "identity_match_method": expected_identity_match_method(candidate, public),
            "strong_identifiers_agree": str(agrees).lower(),
            "source_record_sha256": candidate["source_record_sha256"],
            "identity_resolution_status": identity_status,
            "current_taxonomy": taxonomy_text(public),
            "legacy_category": CATEGORY_BY_DIAGNOSTIC[
                candidate["legacy_scope_category"]
            ],
            "primary_source": review["primary_source"],
            "decisive_datasets_tasks": review["decisive_datasets_tasks"],
            "face_only_flag": face_flag,
            "video_temporal_flag": video_flag,
            "media_scope_status": media_status,
            "mechanism": review["mechanism"],
            "broader_synthetic_image_evidence": review[
                "broader_synthetic_image_evidence"
            ],
            "final_audit_status": review["final_audit_status"],
            "confidence": review["confidence"].lower(),
            "recommended_next_action": review["recommended_next_action"],
            "exact_evidence_needed": exact_question,
            "rationale": review["rationale"],
            "corpus_action": "NONE_AUDIT_ONLY",
        }
        if set(row) != set(FIELDS):
            raise AssertionError("builder fields do not match canonical audit schema")
        rows.append(row)
    validate_rows(rows)
    return rows


def write_artifacts(rows: Sequence[Mapping[str, str]]) -> None:
    integrity = verify_baseline()
    texts = generated_texts(rows, integrity)
    outputs = {
        CSV_PATH: texts[CSV_PATH.name],
        REPORT_PATH: texts[REPORT_PATH.name],
        HIGH_CONFIDENCE_PATH: texts[HIGH_CONFIDENCE_PATH.name],
        NEEDS_REVIEW_PATH: texts[NEEDS_REVIEW_PATH.name],
        VALIDATION_PATH: texts[VALIDATION_PATH.name],
        IDENTITY_SUMMARY_PATH: texts[IDENTITY_SUMMARY_PATH.name],
        ARTIFACT_HASH_PATH: texts[ARTIFACT_HASH_PATH.name],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    verify_baseline()
    verify_workspace_scope()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows = build_rows()
    if args.check:
        if CSV_PATH.read_text(encoding="utf-8") != canonical_csv_text(rows):
            raise AssertionError("canonical audit CSV is stale")
        integrity = verify_baseline()
        texts = generated_texts(rows, integrity)
        for path in (
            REPORT_PATH,
            HIGH_CONFIDENCE_PATH,
            NEEDS_REVIEW_PATH,
            VALIDATION_PATH,
            IDENTITY_SUMMARY_PATH,
            ARTIFACT_HASH_PATH,
        ):
            if path.read_text(encoding="utf-8") != texts[path.name]:
                raise AssertionError(f"stale audit artifact: {path}")
    else:
        write_artifacts(rows)
    print(json.dumps(validate_rows(rows), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
