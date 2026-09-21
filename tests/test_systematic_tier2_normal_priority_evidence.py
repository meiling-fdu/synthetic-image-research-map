"""Integrity checks for the bounded 20-paper Tier 2 NORMAL evidence pass."""

from collections import Counter
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from integrate_systematic_tier2_normal_priority_evidence import (  # noqa: E402
    OUT,
    new_institution_rows,
    paper_id,
)
from report_systematic_tier2_high_priority_evidence import (  # noqa: E402
    corpus_stats as frozen_high_corpus_stats,
    diff_audit as frozen_high_diff_audit,
)
from report_systematic_tier2_normal_priority_evidence import (  # noqa: E402
    CSV_PATH,
    REPORT_PATH,
    corpus_stats,
    diff_audit,
    duplicate_identity_audit,
    expected_rows,
    identity_audit,
    read_csv,
    render,
    validate_lock_receipts,
)
from systematic_tier2_normal_priority_evidence_data import PAPERS  # noqa: E402


def test_all_twenty_questions_have_locked_evidence_outcomes():
    rows = expected_rows()
    assert read_csv(CSV_PATH) == rows
    assert len(rows) == 20
    assert Counter(row["evidence_resolution_outcome"] for row in rows) == {
        "EVIDENCE_CONFIRMS_SCOPE": 9,
        "EVIDENCE_EXCLUDES_SCOPE": 11,
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
    locks = validate_lock_receipts(rows)
    assert locks["evidence"]["rows"] == 20
    assert locks["identity"]["rows"] == 9


def test_scope_exclusions_stay_out_of_both_authoritative_registries():
    rows = expected_rows()
    excluded = {
        row["title"]
        for row in rows
        if row["evidence_resolution_outcome"] == "EVIDENCE_EXCLUDES_SCOPE"
    }
    assert excluded == {
        "M2SFormer: Multi-Spectral and Multi-Scale Attention with Edge-Aware Difficulty Guidance for Image Forgery Localization",
        "AdaIFL: Adaptive Image Forgery Localization via a Dynamic and Importance-aware Transformer Network",
        "IMDL-BenCo: A Comprehensive Benchmark and Codebase for Image Manipulation Detection & Localization",
        "Towards Modern Image Manipulation Localization: A Large-Scale Dataset and Novel Methods",
        "Pre-Training-Free Image Manipulation Localization through Non-Mutually Exclusive Contrastive Learning",
        "Noise-assisted Prompt Learning for Image Forgery Detection and Localization",
        "SAFL-Net: Semantic-Agnostic Feature Learning Network with Auxiliary Plugins for Image Manipulation Detection",
        "Diffusion Models Meet Image Counter-Forensics",
        "Learnable Frequency Decomposition for Image Forgery Detection and Localization",
        "Uncertainty-guided Learning for Improving Image Manipulation Detection",
        "ADCD-Net: Robust Document Image Forgery Localization via Adaptive DCT Feature and Hierarchical Content Disentanglement",
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
        "author_institution_mappings.csv": 21,
        "institutions.csv": 5,
        "institution_location_review.csv": 5,
    }
    assert all(
        values["existing_rows_changed"] == 0
        for values in diff["curated"].values()
    )
    assert diff["public_paper_records"] == {
        "existing_records": 657,
        "existing_records_changed": 0,
        "new_records": 9,
    }
    assert diff["public_marker_records"] == {
        "existing_records": 1494,
        "existing_records_changed": 0,
        "new_records": 14,
    }
    assert diff["frontend"]["changed"] == 0


def test_affiliations_taxonomy_and_location_uncertainty_are_explicit():
    planned = json.loads((OUT / "planned_additions.json").read_text(encoding="utf-8"))
    assert len(planned["papers.csv"]) == 9
    assert len(planned["paper_taxonomy.csv"]) == 9
    assert len(planned["author_institution_mappings.csv"]) == 21
    assert len(planned["institutions.csv"]) == 5
    assert len(planned["institution_location_review.csv"]) == 5
    assert all(
        row["review_status"] == "pending_review"
        and row["coordinate_status"] == "missing"
        for row in planned["institution_location_review.csv"]
    )
    new_ids = {row["institution_id"] for row in new_institution_rows().values()}
    confirmed_locations = read_csv(ROOT / "data/curated/institution_locations.csv")
    assert not new_ids.intersection(row["institution_id"] for row in confirmed_locations)

    by_candidate = {paper["candidate_id"]: paper for paper in PAPERS}
    assert by_candidate["audit:29fa62c1fc9fd79d"]["tasks"] == "detection;source_attribution"
    assert by_candidate["audit:2fa7c05b3b864bfe"]["tasks"] == "localization"
    assert by_candidate["audit:bcd4cedccc0c34eb"]["tasks"] == "localization"
    assert "fully_generated" in by_candidate["audit:b666c0f0f497632a"]["image_scopes"]
    assert all("generative_editing" in paper["image_scopes"] for paper in PAPERS[1:])


def test_final_counts_and_markerless_visibility_are_exact():
    assert corpus_stats() == {
        "public": 666,
        "published": 555,
        "mapped": 645,
        "markers": 1508,
        "added_papers": 9,
        "markerless_added_papers": [
            "ILLUSION: Unveiling Truth with a Comprehensive Multi-Modal, Multi-Lingual Deepfake Dataset"
        ],
    }


def test_frozen_high_predecessor_remains_reproducible():
    assert frozen_high_corpus_stats() == {
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
    assert frozen_high_diff_audit()["public_paper_records"] == {
        "existing_records": 648,
        "existing_records_changed": 0,
        "new_records": 9,
    }


def test_report_reproduces_byte_for_byte():
    rows = read_csv(CSV_PATH)
    assert rows == expected_rows()
    assert REPORT_PATH.read_text(encoding="utf-8") == render(
        rows, corpus_stats(), diff_audit()
    )
