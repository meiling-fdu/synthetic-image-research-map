"""Integrity checks for the bounded 12-paper Tier 2 HIGH evidence pass."""

from collections import Counter
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from integrate_systematic_tier2_high_priority_evidence import (  # noqa: E402
    OUT,
    new_institution_rows,
    paper_id,
)
from report_systematic_tier2_high_priority_evidence import (  # noqa: E402
    CSV_PATH,
    REPORT_PATH,
    corpus_stats,
    diff_audit,
    duplicate_identity_audit,
    expected_rows,
    identity_audit,
    read_csv,
    render,
)
from systematic_tier2_high_priority_evidence_data import PAPERS  # noqa: E402


def test_all_twelve_questions_have_locked_evidence_outcomes():
    rows = expected_rows()
    assert read_csv(CSV_PATH) == rows
    assert len(rows) == 12
    assert Counter(row["evidence_resolution_outcome"] for row in rows) == {
        "EVIDENCE_CONFIRMS_SCOPE": 9,
        "EVIDENCE_EXCLUDES_SCOPE": 3,
    }
    confirmed = [
        row
        for row in rows
        if row["evidence_resolution_outcome"] == "EVIDENCE_CONFIRMS_SCOPE"
    ]
    assert Counter(row["identity_reconciliation_outcome"] for row in confirmed) == {
        "MISSING_ADD": 9
    }
    assert all(row["exact_original_unresolved_question"] for row in rows)
    assert all(row["primary_source"] and row["decisive_evidence"] for row in rows)


def test_scope_exclusions_stay_out_of_both_authoritative_registries():
    rows = expected_rows()
    excluded = {
        row["title"]
        for row in rows
        if row["evidence_resolution_outcome"] == "EVIDENCE_EXCLUDES_SCOPE"
    }
    assert excluded == {
        "DINOv3 Beats Specialized Detectors: A Simple Foundation Model Baseline for Image Forensics",
        "FreDA: Training-Free Test-Time Adaptation for Deepfake Detection via Non-parametric Cache Retrieval",
        "Generating Attribution Reports for Manipulated Facial Images: A Dataset and Baseline",
    }
    public_titles = {
        row["title"]
        for row in json.loads(
            (ROOT / "web/data/public_preview_papers.json").read_text(encoding="utf-8")
        )["records"]
    }
    exclusion_titles = {
        row["title"] for row in read_csv(ROOT / "data/curated/paper_exclusions.csv")
    }
    assert not excluded.intersection(public_titles)
    assert not excluded.intersection(exclusion_titles)


def test_preinsertion_identity_and_final_duplicate_checks_are_clean():
    identities = identity_audit()
    assert len(identities) == 9
    assert all(
        not row["baseline_strong_matches"]
        and not row["active_exclusion_matches"]
        and row["current_matches"] == [paper_id(row["candidate_id"])]
        for row in identities
    )
    assert not any(duplicate_identity_audit().values())


def test_authoritative_append_is_exact_and_preserves_existing_rows():
    diff = diff_audit()
    assert {
        name: values["new_rows"]
        for name, values in diff["curated"].items()
        if values["new_rows"]
    } == {
        "papers.csv": 9,
        "paper_taxonomy.csv": 9,
        "author_institution_mappings.csv": 15,
        "institutions.csv": 6,
        "institution_location_review.csv": 6,
    }
    assert all(
        values["existing_rows_changed"] == 0
        for values in diff["curated"].values()
    )
    assert diff["public_paper_records"] == {
        "existing_records": 648,
        "existing_records_changed": 0,
        "new_records": 9,
    }
    assert diff["public_marker_records"] == {
        "existing_records": 1486,
        "existing_records_changed": 0,
        "new_records": 8,
    }
    assert diff["frontend"]["changed"] == 0


def test_affiliations_taxonomy_and_location_uncertainty_are_explicit():
    planned = json.loads((OUT / "planned_additions.json").read_text(encoding="utf-8"))
    assert len(planned["papers.csv"]) == 9
    assert len(planned["paper_taxonomy.csv"]) == 9
    assert len(planned["author_institution_mappings.csv"]) == 15
    assert len(planned["institutions.csv"]) == 6
    assert len(planned["institution_location_review.csv"]) == 6
    assert all(
        row["review_status"] == "pending_review"
        and row["coordinate_status"] == "missing"
        for row in planned["institution_location_review.csv"]
    )
    new_ids = {row["institution_id"] for row in new_institution_rows().values()}
    confirmed_locations = read_csv(ROOT / "data/curated/institution_locations.csv")
    assert not new_ids.intersection(row["institution_id"] for row in confirmed_locations)

    by_candidate = {paper["candidate_id"]: paper for paper in PAPERS}
    assert by_candidate["audit:07f15e7e8a78398a"]["tasks"] == "source_attribution"
    assert by_candidate["audit:f293e205186b3f59"]["tasks"] == "source_attribution"
    assert by_candidate["audit:f55fbb498b42444f"]["tasks"] == "detection;localization"
    assert "fully_generated" in by_candidate["audit:0b72dded38f87a65"]["image_scopes"]


def test_final_counts_and_markerless_visibility_are_exact():
    assert corpus_stats() == {
        "public": 657,
        "published": 546,
        "mapped": 637,
        "markers": 1494,
        "added_papers": 9,
        "markerless_added_papers": [
            "Abductive Corroboration of Probabilistic AI Models for Forensic Synthetic Media Detection",
            "Conditional Uncertainty-Aware Political Deepfake Detection with Stochastic Convolutional Neural Networks",
            "Deep Learning for CGI and Visual Forgery Detection: A Comprehensive Survey",
            "Detecting Violent Deepfakes: Dataset and a Compact Attention Network with Multi-Scale Supervision",
        ],
    }


def test_report_reproduces_byte_for_byte():
    rows = read_csv(CSV_PATH)
    assert rows == expected_rows()
    assert REPORT_PATH.read_text(encoding="utf-8") == render(
        rows, corpus_stats(), diff_audit()
    )
