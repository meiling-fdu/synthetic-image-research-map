"""Focused integrity tests for the twelve-paper Tier 2 inclusion pass."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from report_systematic_tier2_include import CSV, REPORT, corpus_stats, diff_audit, identity_audit, read_csv, render, rows
from integrate_systematic_tier2_include import NEW, OUT, PAPERS, ROOT

def test_all_twelve_decisions_and_exported_fields():
    expected=rows(); assert len(expected)==12; assert read_csv(CSV)==expected
    assert {r["reconciliation_outcome"] for r in expected}=={"MISSING_ADD"}
    assert len({r["paper_id"] for r in expected})==12

def test_current_identity_and_exclusion_reconciliation_is_clean():
    audit=identity_audit(); assert len(audit)==12
    assert all(not r["strong_matches"] and not r["active_exclusion_matches"] for r in audit)

def test_existing_authoritative_rows_and_frontend_are_unchanged():
    assert all(d["existing_rows_changed"]==0 for n,d in diff_audit().items() if n!="frontend")
    assert diff_audit()["frontend"]["changed"]==0

def test_new_institutions_have_review_rows_but_no_guessed_locations():
    locations=read_csv(ROOT/"data/curated/institution_locations.csv")
    reviews=read_csv(ROOT/"data/curated/institution_location_review.csv")
    ids={r["institution_id"] for r in NEW.values()}
    assert not ids.intersection(r["institution_id"] for r in locations)
    assert ids <= {r["institution_id"] for r in reviews if r["review_status"]=="pending_review"}

def test_author_specific_affiliations_and_taxonomy_are_exact():
    planned=json.loads((OUT/"planned_additions.json").read_text())
    assert len(planned["author_institution_mappings.csv"])==31
    assert len(planned["paper_taxonomy.csv"])==12
    tg=next(p for p in planned["proposals"] if p["cid"]=="audit:07194f58b4540acc")
    assert tg["types"]=="dataset;benchmark;analysis_study" and tg["tasks"]=="detection;localization"
    assert {a["institution"] for a in tg["verified_affiliations"]}=={"Ghent University","imec","Centre for Research and Technology Hellas"}

def test_final_counts_duplicates_exclusions_and_markerless_visibility():
    assert corpus_stats()=={"public":648,"published":538,"mapped":632,"markers":1486,"duplicate_identity_pairs":[],"active_exclusion_leaks":0}
    assert {r["title"] for r in rows() if r["marker_count"]=="0"}=={
        "Detecting AI-Generated Forgeries via Iterative Manifold Deviation Amplification",
        "Scalable Black-Box Model Attribution for Images",
        "ImageTrust: Multi-backbone Fusion for AI-Generated Image Detection with Calibrated Uncertainty",
    }

def test_report_reproduces_byte_for_byte():
    actual=read_csv(CSV); assert REPORT.read_text()==render(actual,corpus_stats(),diff_audit())
